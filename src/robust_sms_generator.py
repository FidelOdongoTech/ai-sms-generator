import requests
import json
import random
from customer_data import get_customer_data

class RobustSMSGenerator:
    def __init__(self, model_name="tinyllama"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"
    
    def _generate_ollama_response(self, prompt, max_tokens=40):
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7, # Increased temperature for more creative variations
                "max_tokens": max_tokens
            }
        }
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=20) # Increased timeout
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            print(f"Ollama API error: {e}")
            return ""

    def generate_template_sms(self, customer_name, loan_balance, due_date, tone="formal"):
        """
        Generate SMS using predefined templates with variations
        """
        templates = {
            "formal": [
                f"Dear {customer_name}, your loan of {loan_balance} is due on {due_date}. Please make payment to avoid penalties. Co-op Bank",
                f"{customer_name}, kindly settle your {loan_balance} loan by {due_date}. Thank you for banking with Co-op Bank.",
                f"Reminder: {customer_name}, your loan balance of {loan_balance} is due {due_date}. Please pay on time. Co-op Bank"
            ],
            "friendly": [
                f"Hi {customer_name}! Friendly reminder: your {loan_balance} loan is due {due_date}. Thanks for choosing Co-op Bank!",
                f"Hello {customer_name}, just a gentle reminder that your {loan_balance} loan payment is due {due_date}. Co-op Bank",
                f"Hey {customer_name}! Your {loan_balance} loan is due {due_date}. We appreciate your business with Co-op Bank!"
            ],
            "urgent": [
                f"URGENT: {customer_name}, your {loan_balance} loan is due {due_date}. Please pay immediately to avoid late fees. Co-op Bank",
                f"{customer_name}, IMPORTANT: Your {loan_balance} loan payment is due {due_date}. Act now to avoid penalties. Co-op Bank",
                f"ATTENTION {customer_name}: {loan_balance} loan due {due_date}. Immediate payment required. Co-op Bank"
            ]
        }
        
        template_list = templates.get(tone, templates["formal"])
        selected_template = random.choice(template_list)
        
        # Ensure under 160 characters
        if len(selected_template) > 160:
            selected_template = selected_template[:157] + "..."
        
        return selected_template
    
    def enhance_with_ai(self, template_sms, customer_name, loan_balance, due_date, tone):
        """
        Try to enhance template SMS with AI, fallback to template if AI fails
        """
        prompt = f"Improve this SMS to be more {tone} while keeping it under 160 characters: \'{template_sms}\'"
        
        enhanced_text = self._generate_ollama_response(prompt)
            
        # Validate the enhanced text
        if (len(enhanced_text) <= 160 and 
            customer_name in enhanced_text and 
            loan_balance in enhanced_text and 
            "Co-op Bank" in enhanced_text):
            return enhanced_text
        else:
            return template_sms

    def paraphrase_sms_template(self, original_sms, customer_name, loan_balance, due_date, tone="formal", count=3):
        """
        Paraphrase a given SMS template into different tones using AI.
        """
        paraphrased_variations = []
        for _ in range(count):
            prompt = (
                f"Paraphrase the following SMS message to be more {tone} in tone. "
                f"Ensure it includes the customer name \'{customer_name}\' (if applicable), "
                f"loan balance \'{loan_balance}\' (if applicable), "
                f"due date \'{due_date}\' (if applicable), and mentions \'Co-op Bank\'. "
                f"Keep the message strictly under 160 characters. "
                f"Original SMS: \'{original_sms}\'"
            )
            paraphrased_sms = self._generate_ollama_response(prompt, max_tokens=50) # Increased max_tokens for paraphrasing
            
            # Basic validation and fallback
            if not paraphrased_sms or len(paraphrased_sms) > 160:
                # If AI fails or generates too long, try a simpler prompt or use original
                simple_prompt = (
                    f"Rewrite this SMS in a {tone} tone, under 160 chars: \'{original_sms}\'"
                )
                paraphrased_sms = self._generate_ollama_response(simple_prompt, max_tokens=50)
                if not paraphrased_sms or len(paraphrased_sms) > 160:
                    paraphrased_sms = original_sms[:157] + "..." if len(original_sms) > 160 else original_sms

            paraphrased_variations.append(paraphrased_sms)
        return paraphrased_variations

    def generate_sms_variations(self, customer_name, loan_balance, due_date, tone="formal", count=3):
        """
        Generate multiple SMS variations using templates and AI enhancement
        """
        variations = []
        
        for i in range(count):
            # Generate template-based SMS
            template_sms = self.generate_template_sms(customer_name, loan_balance, due_date, tone)
            
            # Try to enhance with AI (with fallback to template)
            if i == 0:  # First variation: pure template
                final_sms = template_sms
            else:  # Other variations: try AI enhancement
                final_sms = self.enhance_with_ai(template_sms, customer_name, loan_balance, due_date, tone)
            
            variations.append(final_sms)
        
        return variations
    
    def process_all_customers(self):
        """
        Process all customers and generate SMS messages
        """
        customers = get_customer_data()
        results = []
        
        for customer in customers:
            customer_result = {
                "customer": customer,
                "sms_variations": self.generate_sms_variations(
                    customer["name"],
                    customer["loan_balance"],
                    customer["due_date"],
                    customer["tone"],
                    count=3
                )
            }
            results.append(customer_result)
        
        return results
    
    def export_to_json(self, results, filename="sms_results.json"):
        """
        Export results to JSON file for easy integration with SMS systems
        """
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        return filename

if __name__ == "__main__":
    generator = RobustSMSGenerator()
    
    print("🎯 AI-Powered SMS Generator for Co-op Bank")
    print("=" * 50)
    
    # Test with individual customers
    customers = get_customer_data()
    
    for customer in customers:
        print(f"\n--- Customer: {customer['name']} ---")
        print(f"Loan: {customer['loan_balance']}, Due: {customer['due_date']}, Tone: {customer['tone']}")
        
        variations = generator.generate_sms_variations(
            customer["name"],
            customer["loan_balance"],
            customer["due_date"],
            customer["tone"]
        )
        
        for i, sms in enumerate(variations, 1):
            print(f"SMS {i}: {sms}")
            print(f"       Length: {len(sms)} characters")

    # Test paraphrasing functionality
    print("\n" + "=" * 50)
    print("Testing SMS Paraphrasing...")
    original_sms_template = "Dear Bett, Your loan payment is late by 203 days. Amount in arrears is KES 1,200. Please pay immediately. For inquiry call 0711049000"
    customer_name_for_paraphrase = "Bett"
    loan_balance_for_paraphrase = "KES 1,200"
    due_date_for_paraphrase = "late by 203 days"

    print(f"\n--- Original SMS: {original_sms_template} ---")

    for tone_type in ["formal", "friendly", "urgent"]:
        print(f"\n--- Paraphrasing to {tone_type.capitalize()} Tone ---")
        paraphrased_sms = generator.paraphrase_sms_template(
            original_sms_template,
            customer_name_for_paraphrase,
            loan_balance_for_paraphrase,
            due_date_for_paraphrase,
            tone=tone_type,
            count=3
        )
        for i, sms in enumerate(paraphrased_sms, 1):
            print(f"SMS {i}: {sms}")
            print(f"       Length: {len(sms)} characters")

    
    # Process all customers and export
    print("\n" + "=" * 50)
    print("Processing all customers and exporting to JSON...")
    
    all_results = generator.process_all_customers()
    filename = generator.export_to_json(all_results)
    
    print(f"✅ Results exported to: {filename}")
    print(f"📊 Total customers processed: {len(all_results)}")
    
    # Summary statistics
    total_sms = sum(len(result["sms_variations"]) for result in all_results)
    print(f"📱 Total SMS variations generated: {total_sms}")
    
    print("\n🚀 Ready for integration with SMS systems!")


