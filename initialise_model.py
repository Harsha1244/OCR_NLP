import easyocr
import translators as ts
import os
import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

# Initialize spaCy (change model if necessary)
nlp = spacy.blank("xx")  # Using a blank multi-language model; customize if needed

# Load the T5 model for summarization
model_name = "t5-small"  # You can change this to a larger model if needed
t5_tokenizer = T5Tokenizer.from_pretrained(model_name)
t5_model = T5ForConditionalGeneration.from_pretrained(model_name)

def summarize_with_t5(text):
    # Prepare the input for T5 summarization
    input_ids = t5_tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    # Generate the summary
    summary_ids = t5_model.generate(input_ids, max_length=50, min_length=10, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = t5_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def process_with_spacy(text):
    # Process the text with spaCy to get POS tags
    doc = nlp(text)
    pos_tags = [(token.text, token.pos_) for token in doc]
    return pos_tags

def easy_model(finallist):
    if len(finallist[0]) == 0:
        print("easy_model: No images in folder! Exiting...")
        return
    else:
        reader = easyocr.Reader(['en', 'hi'])  # Initialize EasyOCR with English and Hindi languages
        images = finallist[0]
        count = finallist[1]
        
        for i in range(len(images)):
            filename = os.path.join("images", images[i])  # Create full path for image
            output = reader.readtext(filename, paragraph=True, batch_size=3)
            sans_text = ""
            
            for j in range(len(output)):
                sans_text += " \n" + output[j][1]

            # Summarize the extracted text
            summary = summarize_with_t5(sans_text)
            
            # Perform POS tagging
            pos_tags = process_with_spacy(sans_text)
            print("POS Tags for image {}: {}".format(images[i], pos_tags))

            # Translate the summarized text
            translated_text = ts.google(query_text=summary, to_language='en')

            # Save the translated text to a file
            textfilename = os.path.splitext(images[i])[0].lower()  # Create filename without extension
            with open(os.path.join('results', f'{textfilename}.txt'), 'w', encoding='utf-8') as f:
                f.write(translated_text)

            print("Percentage: " + str(round(((i + 1) / len(images)) * 100, 2)) + "%\r", end="")
        
        input("Task successfully completed! Press Enter to quit...")

# Example usage
if __name__ == "__main__":
    # Replace with your logic to gather the list of images
    finallist = (["image1.jpg", "image2.jpg"], 2)  # Replace with your actual image list
    easy_model(finallist)
