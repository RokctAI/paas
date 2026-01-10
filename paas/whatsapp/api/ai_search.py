
import frappe
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Global cache for the model
_MODEL = None
_PRODUCT_EMBEDDINGS_CACHE = {}  # {shop_id: {'ids': [], 'embeddings': Tensor, 'metadata': []}}

def get_model():
    """
    Lazy loads the MiniLM model from the local path defined in setup_ai.py
    """
    global _MODEL
    if _MODEL is None:
        # Try to find the local model path from site config or default
        model_path = frappe.conf.get("ai_model_path") or "/opt/rokct_models"
        minilm_path = os.path.join(model_path, "minilm")
        
        try:
            if os.path.exists(minilm_path):
                print(f"🧠 Loading local AI model from {minilm_path}...")
                _MODEL = SentenceTransformer(minilm_path)
            else:
                print(f"⚠️ Local model not found at {minilm_path}. Downloading from Hub...")
                # Fallback to downloading/caching from Hub
                _MODEL = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ AI Model Loaded.")
        except Exception as e:
            frappe.log_error(f"Failed to load AI Model: {e}")
            return None
    return _MODEL

def index_factory(shop_id):
    """
    Fetches products for a shop and creates embeddings.
    Returns the cache entry.
    """
    # Check cache first
    if shop_id in _PRODUCT_EMBEDDINGS_CACHE:
        return _PRODUCT_EMBEDDINGS_CACHE[shop_id]
        
    model = get_model()
    if not model:
        return None
        
    # Fetch active products for the shop
    products = frappe.get_all("Product", 
                             filters={"shop_id": shop_id, "active": 1},
                             fields=["name", "title", "description", "uuid"])
    
    if not products:
        return None
        
    # Prepare texts to embed (Title + Description)
    texts = [f"{p['title']} {p.get('description') or ''}" for p in products]
    
    # Compute embeddings
    print(f"🧠 Indexing {len(texts)} products for shop {shop_id}...")
    embeddings = model.encode(texts, convert_to_tensor=True)
    
    # Store in cache
    cache_entry = {
        'ids': [p['name'] for p in products], # DocNames
        'uuids': [p['uuid'] for p in products],
        'titles': [p['title'] for p in products],
        'embeddings': embeddings
    }
    _PRODUCT_EMBEDDINGS_CACHE[shop_id] = cache_entry
    return cache_entry

def semantic_search(query, shop_id, top_k=3):
    """
    Performs semantic search for the query within the shop's products.
    """
    model = get_model()
    if not model:
        return []

    # Ensure index exists
    index = index_factory(shop_id)
    if not index:
        return []
        
    # Embed query
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # helper for cosine similarity
    # util.cos_sim returns [[score1, score2...]]
    scores = util.cos_sim(query_embedding, index['embeddings'])[0]
    
    # Get top k results
    # torch.topk returns (values, indices)
    top_results = list(zip(scores.tolist(), range(len(scores))))
    
    # Sort by score descending
    top_results.sort(key=lambda x: x[0], reverse=True)
    top_results = top_results[:top_k]
    
    results = []
    for score, idx in top_results:
        if score < 0.3: # Threshold
            continue
            
        results.append({
            'name': index['ids'][idx],
            'uuid': index['uuids'][idx],
            'title': index['titles'][idx],
            'score': score
        })
        
    return results

# --- NLP & Intent Logic ---

# --- NLP & Intent Logic ---

def load_intents_from_config():
    """
    Loads intents from rokct/ai_config/customer_intents.json
    """
    import json
    
    try:
        # Robust way: Get path relative to the 'rokct' app module
        path = frappe.get_app_path("brain", "ai_config", "customer_intents.json")
    except Exception as e:
        print(f"⚠️ Could not resolve app path for 'rokct': {e}")
        return get_fallback_intents()
        
    if not os.path.exists(path):
        print(f"⚠️ Intent Config not found at {path}. Using fallbacks.")
        return get_fallback_intents()
        
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            anchors = data.get('anchors', {})
            
            # Convert "key": "word1 word2" -> "key": ["word1", "word2"]
            prototypes = {}
            for key, val in anchors.items():
                prototypes[key] = val.split(" ")
                
            return prototypes
    except Exception as e:
        print(f"❌ Failed to parse intent config: {e}")
        return get_fallback_intents()

def get_fallback_intents():
    return {
        "action_buy": ["buy", "order", "purchase", "get", "add"],
        "action_find": ["find", "search", "show", "list", "view"],
        "action_track": ["track", "where", "status"],
        "misc_greeting": ["hi", "hello", "menu"]
    }

# Cache for intent embeddings
_INTENT_EMBEDDINGS = None

def get_intent_embeddings():
    global _INTENT_EMBEDDINGS
    if _INTENT_EMBEDDINGS:
        return _INTENT_EMBEDDINGS
        
    model = get_model()
    if not model: return None
    
    prototypes = load_intents_from_config()
    
    _INTENT_EMBEDDINGS = {}
    print("🧠 Indexing Intent Prototypes from Config...")
    for intent, sentences in prototypes.items():
        _INTENT_EMBEDDINGS[intent] = model.encode(sentences, convert_to_tensor=True)
        
    return _INTENT_EMBEDDINGS

def classify_intent(text):
    """
    Classifies text into one of the INTENT_PROTOTYPES keys.
    Returns (intent, score).
    """
    model = get_model()
    intent_map = get_intent_embeddings()
    if not model or not intent_map:
        return "unknown", 0.0
        
    # Embed query
    query_emb = model.encode(text, convert_to_tensor=True)
    
    best_intent = "unknown"
    best_score = 0.0
    
    for intent, prototypes in intent_map.items():
        # Compute similarity with all prototypes for this intent
        scores = util.cos_sim(query_emb, prototypes)[0]
        max_score = float(scores.max()) # Best match among the prototypes
        
        if max_score > best_score:
            best_score = max_score
            best_intent = intent
            
    return best_intent, best_score

def extract_entity(text, intent):
    """
    Extracts the 'entity' (keywords) from the text by removing common action words/stopwords.
    Simple heuristic since we don't have a NER model.
    """
    # Common stopwords/action words to strip
    STOP_PHRASES = [
        "i want to", "i want", "can i get", "give me", "buy", "purchase", "order", "find", "search for", 
        "show me", "looking for", "get", "add to cart", "please", "some", "a", "an", "the"
    ]
    
    clean_text = text.lower().strip()
    
    # Simple iterative strip (not perfect but fast)
    # Sort phrases by length desc to remove longest first ("i want to" before "i want")
    sorted_stops = sorted(STOP_PHRASES, key=len, reverse=True)
    
    for phrase in sorted_stops:
        if clean_text.startswith(phrase + " "):
            clean_text = clean_text[len(phrase)+1:]
        elif clean_text.startswith(phrase):
             clean_text = clean_text[len(phrase):]
             
    return clean_text.strip()

def search_global_shops(query):
    """
    Searches for Shops matching the query (Name or Category or Description).
    """
    # 1. SQL Search (Simple/Fuzzy)
    shops = frappe.db.sql(f"""
        SELECT name, uuid, description, logo_img, back_img
        FROM `tabShop`
        WHERE status='Approved' 
        AND (shop_type != 'Ecommerce' AND is_ecommerce = 0)
        AND (
            name LIKE %s OR 
            description LIKE %s OR
            uuid IN (
                SELECT parent FROM `tabShop Category` WHERE name LIKE %s
            )
        )
        LIMIT 5
    """, (f"%{query}%", f"%{query}%", f"%{query}%"), as_dict=True)
    
    return shops

