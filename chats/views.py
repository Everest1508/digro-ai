from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Chat, Message
import json
import google.generativeai as genai
import os
import subprocess
from django.core.files import File


# Configure your API key here
genai.configure(api_key="AIzaSyD0EFExVF1KUbF2BIjPV6CArpDhaLxDpig")

def get_gemini_response(input_text):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(input_text)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return "I'm having trouble responding right now."

@login_required
def chat_view(request):
    chat = Chat.objects.create(user=request.user)
    return redirect(f'/chat/{chat.uuid}/')

@login_required
def uuid_chat(request, uuid):
    chat = get_object_or_404(Chat, user=request.user, uuid=uuid)
    messages = chat.messages.all().order_by('created_at')
    return render(request, 'chat/index.html', {'chat': chat, 'messages': messages})

def get_ai_response(user_input):
    prompt = f'''
    Please generate PlantUML code based on the following description and provide a summary explanation of the code's structure and functionality. Respond in JSON format with three fields: plant_uml_code for the generated PlantUML code, description for the explanation, and is_diagram indicating whether the request is for a diagram.

    Description: {user_input}

    Output format:
    {{
      "plant_uml_code": "/* Your generated PlantUML code here */",
      "description": "A brief explanation of the generated PlantUML diagram.",
      "is_diagram": /* true if user asked for a diagram, false if text */
    }}
    
    Ensure that the PlantUML code accurately represents the description provided and is valid for rendering a diagram.
    '''
    return get_gemini_response(prompt)

@login_required
def chat_api(request):
    if request.method == 'POST':
        # try:
        data = json.loads(request.body)
        user_message = data.get('message')
        chat_uuid = data.get('chat_uuid')

        if not user_message or not chat_uuid:
            return JsonResponse({'success': False, 'error': 'Message or chat UUID missing.'}, status=400)

        chat = get_object_or_404(Chat, uuid=chat_uuid, user=request.user)

        Message.objects.create(chat=chat, content=user_message, sender='user')

        ai_response = get_ai_response(user_message)
        
        ai_response_json = json.loads(ai_response.replace("```JSON", "").replace("```json", "").replace("```", ""))

        Message.objects.create(chat=chat, content=ai_response_json['description'], sender='ai')

        if ai_response_json.get('is_diagram'):
            plant_uml_code = ai_response_json['plant_uml_code']
            prompt = f'''
            I have the following PlantUML code. Please check its correctness. If the code is incorrect, provide the corrected version. If it is correct, simply return a more detailed version of the same code.

            Code:
            {plant_uml_code}
            Output format:
            Only the PlantUML code should be returned.
            Avoid any explanations, comments, or additional text.'''

            corrected_code, error_found = check_and_correct_plantuml_code(prompt, chat.uuid)
            print(error_found)

            if not error_found:
                write_plant_uml_to_file(corrected_code, chat.uuid)

                relative_image_path = f'uml_files/plant_uml_{chat.uuid}.png'
                # os.remove(f'uml_files/plant_uml_{chat.uuid}.txt')


                with open(relative_image_path, 'rb') as img_file:
                    message = Message(chat=chat, image=File(img_file), is_image=True, sender='ai')
                    message.save()
                    # os.remove(relative_image_path)

                return JsonResponse({
                    'success': True,
                    'plant_uml_code': message.image.url,
                    'description': ai_response_json['description']
                })

            Message.objects.create(chat=chat, content="Failed to generate valid PlantUML code.", sender='ai')
            return JsonResponse({'success': False, 'error': 'Failed to generate valid PlantUML code.'})

        else:
            return JsonResponse({
                'success': True,
                'description': ai_response_json['description']
            })


        # except json.JSONDecodeError:
        #     return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        # except Exception as e:
        #     return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def check_and_correct_plantuml_code(prompt, chat_uuid):
    attempts = 0
    max_attempts = 10  # Limit the number of attempts to avoid infinite loops
    error_found = True
    corrected_code = ""

    while error_found and attempts < max_attempts:
        attempts += 1
        print(f"\nAttempt {attempts}: Checking PlantUML code...")
        
        response = get_gemini_response(prompt)
        corrected_code = response.strip()

        # Save the corrected code to a file
        write_plant_uml_to_file(corrected_code, chat_uuid)

        # Run the PlantUML command to verify the correctness
        result = subprocess.run(['java', '-jar', 'pl.jar', f'uml_files/plant_uml_{chat_uuid}.txt'], capture_output=True, text=True)

        if result.returncode == 0:
            print("PlantUML code is valid. Image generated successfully!")
            error_found = False
        else:
            print(f"Error occurred:\n{result.stderr}")
            print("Attempting to correct the PlantUML code...")
            error_text=""
            if attempts!=1:
               print("ytu")
               error_text= f"""Error While compile:
                                {result.stderr}"""

            prompt = f'''
            I have the following PlantUML code. Please check its correctness. If the code is incorrect, provide the corrected version. If it is correct, simply return a more detailed version of the same code.

            Code:
            {corrected_code}

            {error_text}
            Output format:
            Only the PlantUML code should be returned.
            Avoid any explanations, comments, or additional text.'''

    return corrected_code, error_found

def write_plant_uml_to_file(plant_uml_code, chat_uuid):
    directory = 'uml_files'
    os.makedirs(directory, exist_ok=True)

    file_name = f'{directory}/plant_uml_{chat_uuid}.txt'
    
    with open(file_name, 'w') as f:
        f.write(plant_uml_code)
        
