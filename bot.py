from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'rusyagelirseninam1nakoyar9392'  # Güvenli bir secret key kullanın

# reCAPTCHA anahtarlarınızı buraya girin
RECAPTCHA_SITE_KEY = '6LeZbdwrAAAAAJiGDLXDhGDQYR7tP47Ew0DivbXm'
RECAPTCHA_SECRET_KEY = '6LeZbdwrAAAAAL-Bfj649b4c-VOlRZNexx5Ibapr'

@app.route('/')
def index():
    # Eğer reCAPTCHA doğrulanmışsa index sayfasını göster
    if session.get('recaptcha_verified'):
        return render_template('index.html')
    else:
        # Doğrulanmamışsa reCAPTCHA sayfasına yönlendir
        return redirect(url_for('robot_dogrulama'))

@app.route('/robot-dogrulama', methods=['GET', 'POST'])
def robot_dogrulama():
    if request.method == 'POST':
        # reCAPTCHA doğrulama
        recaptcha_response = request.form.get('g-recaptcha-response')
        
        if recaptcha_response:
            # Google reCAPTCHA doğrulama isteği
            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            data = {
                'secret': RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            
            response = requests.post(verify_url, data=data)
            result = response.json()
            
            if result.get('success'):
                # reCAPTCHA başarılı
                session['recaptcha_verified'] = True
                return redirect(url_for('index'))
            else:
                # reCAPTCHA başarısız
                error_message = "reCAPTCHA doğrulaması başarısız. Lütfen tekrar deneyin."
                return render_template('robot_dogrulama.html', 
                                    site_key=RECAPTCHA_SITE_KEY,
                                    error_message=error_message)
        else:
            # reCAPTCHA yanıtı yok
            error_message = "Lütfen reCAPTCHA'yı doğrulayın."
            return render_template('robot_dogrulama.html', 
                                site_key=RECAPTCHA_SITE_KEY,
                                error_message=error_message)
    
    # GET isteği için reCAPTCHA sayfasını göster
    return render_template('robot_dogrulama.html', site_key=RECAPTCHA_SITE_KEY)

@app.route('/logout')
def logout():
    # Oturumu temizle
    session.pop('recaptcha_verified', None)
    return redirect(url_for('robot_dogrulama'))

# API test endpoint'i
@app.route('/api/test/<api_name>')
def test_api(api_name):
    if not session.get('recaptcha_verified'):
        return redirect(url_for('robot_dogrulama'))
    
    # API test işlemleri burada yapılabilir
    return f"{api_name} API testi başlatılıyor..."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
