# 🌱 SmartDoc OCR System

SmartDoc is an AI-powered **OCR** (Optical Character Recognition) system that converts images of printed or handwritten text into machine-readable text.  
It is designed to digitize documents and support automation and data processing workflows, making historical, technical, and business documents easier to search and analyze. 

---

## 🧾 What Is SmartDoc?

- SmartDoc is an OCR system used to convert document images into text.
- OCR stands for Optical Character Recognition, a technology for recognizing text inside images.   
- It is an AI technology that turns images of text into machine-readable text for downstream processing.  
- It is used to digitize printed or handwritten documents for storage, search, and automation.   
- It plays an important role in automation and data processing, reducing manual data entry. 

---

## 🎯 PEAS Model

**P – Performance Measure**

- Accuracy of recognized text.  
- Speed of processing.   
- Error rate in recognized characters/words. 

**E – Environment**

- Scanned documents.  
- Printed or handwritten text.   
- Images and PDFs. 

**A – Actuators**

- Display recognized text to the user.  
- Save text as files (PDF, Word, TXT, etc.). 

**S – Sensors**

- Scanner for physical documents.  
- Camera for photos of notes or documents.   
- Image input files uploaded from local storage. 

---

## 🧠 AI Techniques Used

- **Machine Learning** – Learns patterns from labeled text-image data to improve recognition.  
- **Deep Learning** – Uses multi-layer neural networks for robust character and word recognition.  
- **Convolutional Neural Networks (CNN)** – Specialized for image-based tasks such as character and text-region detection.  
- **Natural Language Processing (NLP)** – Cleans, corrects, and organizes text, and can help with context-aware error correction. 

---

## 🔁 OCR Workflow

1. **Input Image** – A scanned document or image is provided to the OCR system.   
2. **Pre-processing** – The image is cleaned (e.g., noise removal, binarization, normalization) and prepared for recognition. 
3. **Feature Extraction** – Important text features, such as strokes, shapes, and contours, are identified.   
4. **Classification** – Characters or text segments are recognized using trained AI models.   
5. **Post-processing** – Detected text is grouped, errors are corrected, and layout is organized.   
6. **Output** – Final readable and editable text is produced for display or export. 

---

## 🧪 Example SmartDoc Flow (Scenario)

- The system scans a handwritten or printed document and enhances the image for readability. 
- It detects text regions and runs OCR to extract meaningful content, even from cursive or uneven handwriting.   
- Key information (titles, dates, entities, events) is extracted and structured as machine-readable data.   
- Risk or confidence scores may be assigned to extractions to prioritize human review when needed.  
- Validation rules can be applied to ensure accuracy and consistency before exporting the final data. 
- Once validated, the processed data is ready for export, reporting, or further analysis. 

---

## 🛠 Prerequisites

- Node.js  
- npm (comes with most Node.js installations).  
- A valid `GEMINI_API_KEY` for the AI/OCR backend used by the app. 

---

## 🚀 How to Run the Code

1. **Install dependencies**

   ```bash
   npm install


2. **Run**

   ```bash
   npm run dev
  
