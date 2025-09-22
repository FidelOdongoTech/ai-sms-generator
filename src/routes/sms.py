from flask import Blueprint, request, jsonify
from src.robust_sms_generator import RobustSMSGenerator
from src.customer_data import get_customer_data

sms_bp = Blueprint('sms', __name__)

# Initialize the SMS generator
generator = RobustSMSGenerator()

@sms_bp.route('/generate', methods=['POST'])
def generate_sms():
    """
    Generate SMS for a single customer
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'loan_balance', 'due_date', 'tone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate SMS variations
        variations = generator.generate_sms_variations(
            data['name'],
            data['loan_balance'],
            data['due_date'],
            data['tone'],
            count=3
        )
        
        return jsonify({
            'success': True,
            'customer': data,
            'sms_variations': variations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/generate-all', methods=['GET'])
def generate_all_sms():
    """
    Generate SMS for all predefined customers
    """
    try:
        results = generator.process_all_customers()
        return jsonify({
            'success': True,
            'results': results,
            'total_customers': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/customers', methods=['GET'])
def get_customers():
    """
    Get all predefined customers
    """
    try:
        customers = get_customer_data()
        return jsonify({
            'success': True,
            'customers': customers
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/tones', methods=['GET'])
def get_tones():
    """
    Get available tone options
    """
    return jsonify({
        'success': True,
        'tones': ['formal', 'friendly', 'urgent']
    })

