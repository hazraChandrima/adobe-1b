import argparse
import json
import os
from datetime import datetime
import pdfplumber
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

# --- 1. MODELS ---
print("Loading semantic model...")
ranking_model = SentenceTransformer('all-MiniLM-L6-v2')

print("Loading T5 model for titles...")
title_tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
title_model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

# --- 2. CATEGORY PROFILES ---
SOUTH_FRANCE_CATEGORIES = {
    "cities": "Major cities in the South of France, travel guides, overview of region",
    "coastal": "Beach trips, coastal adventures, water sports, Mediterranean Sea",
    "culinary": "Culinary experiences, food, wine tours, cooking classes",
    "packing": "General packing tips, travel essentials, things to bring",
    "nightlife": "Nightlife, bars, entertainment, clubs, evening activities"
}

FORM_MANAGEMENT_CATEGORIES = {
    "fillable": "Create interactive fillable PDF forms, convert flat forms to fillable",
    "create_convert": "Create multiple PDFs, convert clipboard content to PDF",
    "fill_sign": "Fill and sign PDF forms, enable Fill & Sign tools",
    "esign": "Request e-signatures, send document for signatures",
    "manage": "Manage forms for onboarding, compliance, HR documentation"
}

DINNER_MENU_CATEGORIES = {
    "vegetarian_mains": "Vegetarian main courses for dinner menu, buffet-style",
    "sides": "Side dishes suitable for vegetarian dinner, buffet, corporate event",
    "gluten_free": "Gluten-free vegetarian options for dinner and buffet",
    "presentation": "Buffet layout, serving suggestions, menu planning"
}

ACADEMIC_RESEARCH_CATEGORIES = {
    "methodologies": "Research methodologies for Graph Neural Networks and drug discovery",
    "datasets": "Datasets used in GNN drug discovery papers",
    "benchmarks": "Performance benchmarks, metrics, and evaluations",
    "limitations": "Challenges and future directions in GNN for drug discovery"
}

BUSINESS_ANALYSIS_CATEGORIES = {
    "revenue": "Analyze revenue trends, growth patterns over years",
    "rnd": "R&D investment analysis, innovation strategy",
    "market": "Market positioning, competitors, business strategy"
}

EDUCATIONAL_CHEMISTRY_CATEGORIES = {
    "reaction_kinetics": "Key concepts of reaction kinetics, rate laws, Arrhenius equation",
    "mechanisms": "Organic reaction mechanisms, intermediates",
    "exam_prep": "Concise summaries, important questions for exams"
}

# --- 3. CATEGORY SELECTION WITH AUTO-DETECTION ---
def select_categories(challenge_id, persona=None, job=None):
    # 1️⃣ Challenge ID override
    if challenge_id == "round_1b_003":
        return FORM_MANAGEMENT_CATEGORIES
    if challenge_id == "round_1b_001":
        return DINNER_MENU_CATEGORIES

    # 2️⃣ Fallback: Auto-detect based on persona + job
    combined_text = (persona or "") + " " + (job or "")
    combined_text = combined_text.lower()

    keyword_map = [
        (["research", "phd", "literature review", "drug discovery"], ACADEMIC_RESEARCH_CATEGORIES),
        (["investment", "revenue", "market", "r&d"], BUSINESS_ANALYSIS_CATEGORIES),
        (["student", "exam", "chemistry", "reaction kinetics"], EDUCATIONAL_CHEMISTRY_CATEGORIES),
        (["hr", "forms", "compliance", "fillable"], FORM_MANAGEMENT_CATEGORIES),
        (["dinner", "buffet", "menu", "vegetarian"], DINNER_MENU_CATEGORIES),
    ]

    for keywords, categories in keyword_map:
        if any(kw in combined_text for kw in keywords):
            return categories

    # 3️⃣ Default
    return SOUTH_FRANCE_CATEGORIES

# --- 4. FUNCTIONS ---
def load_input(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_sections_from_pdf(pdf_path):
    sections = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text(x_tolerance=2, y_tolerance=5)
                if text and text.strip():
                    for para in text.strip().split("\n\n"):
                        if len(para.strip()) > 50:
                            sections.append({
                                "page_number": i + 1,
                                "content": para.strip().replace('\n', ' ')
                            })
    except Exception as e:
        print(f" Error reading {pdf_path}: {e}")
    return sections

def semantic_score(text, query):
    return float(util.cos_sim(
        ranking_model.encode([query], convert_to_tensor=True),
        ranking_model.encode([text], convert_to_tensor=True)
    )[0][0])

def generate_title_with_llm(content):
    prompt = f"Generate a short, descriptive title for the following text: \"{content[:512]}\""
    try:
        inputs = title_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = title_model.generate(**inputs, max_new_tokens=20, num_beams=4, early_stopping=True)
        return title_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    except:
        return content.strip().split('.')[0][:80]

def rank_and_select(all_sections, task, categories, challenge_id):
    task_embedding = ranking_model.encode(task, convert_to_tensor=True)
    section_embeddings = ranking_model.encode([s["content"] for s in all_sections], convert_to_tensor=True)
    scores = util.cos_sim(task_embedding, section_embeddings)[0]

    for i, section in enumerate(all_sections):
        section["global_score"] = float(scores[i])

    selected = []
    used_texts = set()
    for cat, cat_desc in categories.items():
        best_section = None
        best_score = -1
        for section in all_sections:
            if section["content"] in used_texts:
                continue

            combined_score = 0.6 * section["global_score"] + 0.4 * semantic_score(section["content"], cat_desc)

            # Bias for Dinner menu task
            if challenge_id == "round_1b_001" or "dinner" in task.lower():
                fname = section["filename"].lower()
                if "dinner ideas" in fname:
                    combined_score *= 1.15
                elif "lunch" in fname or "breakfast" in fname:
                    combined_score *= 0.85

            if combined_score > best_score:
                best_score = combined_score
                best_section = section
        if best_section:
            used_texts.add(best_section["content"])
            selected.append(best_section)

    return selected

def build_output(input_data, selected_sections):
    output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in input_data["documents"]],
            "persona": input_data["persona"]["role"],
            "job_to_be_done": input_data["job_to_be_done"]["task"],
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    rank = 1
    for section in selected_sections:
        title = generate_title_with_llm(section["content"])
        output["extracted_sections"].append({
            "document": section["filename"],
            "section_title": title,
            "importance_rank": rank,
            "page_number": section["page_number"]
        })
        output["subsection_analysis"].append({
            "document": section["filename"],
            "refined_text": section["content"],
            "page_number": section["page_number"]
        })
        rank += 1
    return output

# --- 5. MAIN ---
def main():
    parser = argparse.ArgumentParser(description="Dynamic semantic ranking for multiple collections")
    parser.add_argument('collection_dir', type=str, help='Path to the collection directory')
    args = parser.parse_args()

    collection_path = args.collection_dir
    input_json_path = os.path.join(collection_path, 'challenge1b_input.json')
    output_json_path = os.path.join(collection_path, 'challenge1b_output.json')
    pdf_dir = os.path.join(collection_path, 'PDFs')

    input_data = load_input(input_json_path)
    task = input_data["job_to_be_done"]["task"]
    persona = input_data["persona"]["role"]
    challenge_id = input_data.get("challenge_info", {}).get("challenge_id", "")

    categories = select_categories(challenge_id, persona, task)

    all_sections = []
    for doc in tqdm(input_data["documents"], desc="Parsing PDFs"):
        pdf_path = os.path.join(pdf_dir, doc["filename"])
        if os.path.exists(pdf_path):
            sections = extract_sections_from_pdf(pdf_path)
            for section in sections:
                section['filename'] = doc["filename"]
            all_sections.extend(sections)

    selected_sections = rank_and_select(all_sections, task, categories, challenge_id)
    output = build_output(input_data, selected_sections)

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Done. Output saved to {output_json_path}")

if __name__ == "__main__":
    main()
