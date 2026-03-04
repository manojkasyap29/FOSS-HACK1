# 🔍 NutriScan - Smart Snack Ingredient Analyzer

> **Scan the label. Know your food. Eat better.** 
> A FOSS Hack project that demystifies food labels, identifies harmful ingredients, and helps you make healthier choices instantly.

---

## 🎯 What is NutriScan?

Ever looked at the back of a snack packet and wondered what "E621" or "Maltodextrin" actually is? **NutriScan** is an open-source tool that lets you scan the back of any food product using your camera. It automatically extracts the ingredient list, cross-references it with public nutritional datasets, and tells you exactly what you are putting into your body.

No corporate jargon. No hidden sugars. Just simple, readable facts.

---

## ✨ Features

### Current Features (MVP)
*   📷 **Camera-Based Scanning**: Snap a picture of any ingredient label for immediate extraction.
*   🔍 **Automatic Ingredient Parsing**: Uses robust OCR and NLP to read and understand complex, messy ingredient lists.
*   ⚠️ **Personalization & Allergy Alerts**: Set up a custom profile (e.g., "Vegan", "Nut Allergy", "Keto", "Low Sodium"). If a scanned product violates your dietary needs, the app instantly flags it.
*   🥗 **Healthy Alternatives Recommendation**: If a snack gets a poor health verdict, NutriScan suggests 2-3 healthier open-source/community-curated alternatives in the same category.
*   📊 **Nutritional Verdict**: Gives a clear "Healthy / Moderate / Unhealthy" score based on standardized nutritional benchmarks.

### RoadMap: Future Enhancements
*   🔒 **Privacy-First / Offline Mode**: We plan to move OCR and data matching entirely on-device using local models and an offline SQLite database. Your dietary habits stay on your phone.
*   🌍 **Crowdsourced Database**: Allowing users to manually add missing products or correct OCR errors to build a public good, similar to Open Food Facts but focusing on ingredient flag mapping.

---

## ⚙️ How It Works (Architecture Flow)

```text
📸 User Action       🤖 Core Engine                             📂 Data & Output
-------------       -------------                             ----------------
[ Mobile App ] ---> [ Tesseract OCR ] ---> [ NLP Text Cleaning ] ---> [ Ingredient DB Match ]
(Image Scan)        (Extracts Text)        (Extracts Items)           (Checks for flags/allergens)
                                                                            |
                                                                            v
[ User Screen ] <------------------------------------------------- [ Health Analysis Engine ]
(Verdict, Alerts,                                                  (Calculates Score,
 Alternatives)                                                      Finds Alternatives)
```

1. **Scan**: The user captures an image of the ingredient list.
2. **Extract & Clean**: The image is processed through OCR, and the raw text is cleaned using NLP to identify individual ingredients.
3. **Analyze**: The parsed ingredients are checked against our database and the user's personal dietary profile.
4. **Report**: The system calculates a final health score, highlights any allergens or red flags, and offers better alternatives if necessary.

---

## 🛠️ Tech Stack & Justification

| Component | Technology | Why we chose it |
| :--- | :--- | :--- |
| **OCR / Image Processing** | Tesseract OCR / OpenCV | Open-source, reliable text extraction that can be optimized for mobile or quick backend processing. |
| **Database/Datasets** | Open Food Facts / Kaggle | Comprehensive, community-driven nutritional data to map ingredients to their health impacts. |
| **Backend** | Python / FastAPI | Fast, lightweight, and excellent for serving ML/NLP endpoints. |
| **Frontend** | React / Flutter (TBD) | Cross-platform flexibility so users can scan from any device. |
| **ML / NLP** | spaCy / scikit-learn | Efficiently parsing unstructured text (like "Contains 2% or less of...") into clean data arrays. |

---

## 🚀 Getting Started (Local Development)

*(Note: These are placeholder instructions while the project is in active development)*

### Prerequisites
*   Python 3.10+
*   Node.js (for frontend)
*   Tesseract OCR installed on your system

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/nutriscan.git
   cd nutriscan
   ```

2. **Set up the Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Set up the Frontend:**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

4. **Run the App:** Open `http://localhost:3000` in your browser.

---

## 🤝 Contributing
As a FOSS Hack project, we believe in building tools that empower users. Contributions, new feature ideas, and dataset improvements are more than welcome!
*   Found a bug? Open an Issue.
*   Have a dataset? Submit a PR.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
