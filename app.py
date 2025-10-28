import matplotlib
matplotlib.use('Agg')  # Use non-GUI Agg backend
from flask import Flask, render_template, request, session, redirect, url_for
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
from helpers import generate_keypair, encapsulate, decapsulate, encrypt, decrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key in production
app.permanent_session_lifetime = 3600  # Set session timeout to 1 hour (3600 seconds)

# Ensure static directory exists
os.makedirs('static', exist_ok=True)

# Static content
readme_content = """
<h2>README</h2>
<p>This is an educational visualization and simulation platform for Lattice-based Post-Quantum Cryptography (PQC) using the Learning With Errors (LWE) concept.</p>
<ul>
    <li><strong>Features:</strong> Interactive 3D lattice visualization, simulated PKI + KEM handshake, encrypted message exchange.</li>
    <li><strong>Installation:</strong> Clone the repository, install dependencies with `pip3 install flask numpy matplotlib`, and run `python3 app.py`.</li>
    <li><strong>Usage:</strong> Access at `http://127.0.0.1:5000`, adjust parameters, and explore the demo.</li>
</ul>
"""

quantum_content = """
<h2>Quantum Computing Definitions, Keywords, and Key Concepts</h2>
<ul>
    <li><strong>Quantum Bit (Qubit):</strong> The basic unit of quantum information, unlike classical bits, it can exist in superposition of 0 and 1.</li>
    <li><strong>Superposition:</strong> A principle allowing qubits to be in multiple states simultaneously until measured.</li>
    <li><strong>Entanglement:</strong> A quantum phenomenon where qubits become correlated, affecting each other instantaneously regardless of distance.</li>
    <li><strong>Quantum Gate:</strong> Operations on qubits, analogous to classical logic gates, e.g., Hadamard or CNOT gates.</li>
    <li><strong>Post-Quantum Cryptography (PQC):</strong> Cryptographic algorithms resistant to quantum computer attacks, like Lattice-based methods.</li>
    <li><strong>Learning With Errors (LWE):</strong> A problem used in PQC, leveraging noise in lattice structures for security.</li>
</ul>
"""

about_content = """
<h2>About This Project</h2>
<p>This PQC Flask App is an educational tool designed to visualize and simulate Lattice-based Post-Quantum Cryptography using the Learning With Errors (LWE) concept. It aims to help learners and engineers understand how post-quantum key exchange works at a conceptual level, demonstrating secure communication in a quantum-resistant future.</p>
<p><strong>Purpose:</strong> To simplify PQC fundamentals through interactive 3D lattices, handshakes, and cryptographic comparisons, fostering insight into quantum-safe security.</p>

<h2>About the Cybersecurity Expert</h2>
<p>This project is developed by <strong>Robert Kuschel</strong>, a dedicated cybersecurity professional with expertise in quantum-resistant cryptography. Visit his website at <a href="https://robkuschel.com" target="_blank">https://robkuschel.com</a> for more information about his work and contributions to the field.</p>
"""

# Valid password
VALID_PASSWORD = "~QCC2025!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == VALID_PASSWORD:
            session['authenticated'] = True
            session.permanent = True  # Make session permanent with the defined lifetime
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Incorrect password. Please try again.")
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    # Default parameters
    n = 3  # Lattice dimension
    q = 101  # Increased modulus for better granularity
    noise_scale = 0.05  # Reduced noise to improve success
    message = "Hello, PQC!"

    if request.method == 'POST':
        n = int(request.form.get('n', n))
        q = int(request.form.get('q', q))
        noise_scale = float(request.form.get('noise_scale', noise_scale))
        message = request.form.get('message', message)
        n = max(2, min(n, 5))  # Constrain n between 2 and 5 for 3D plotting

    # Debug: Print n and A shape
    print(f"n: {n}")

    # Generate cryptographic components
    A, s, b = generate_keypair(n, q, noise_scale)
    print(f"A shape: {A.shape}, s shape: {s.shape}, b shape: {b.shape}")
    r = np.random.randint(0, q, size=(n, 1))  # Random vector for encapsulation
    u, v, ss_alice = encapsulate(A, b, q, noise_scale, r)
    v_prime, ss_bob = decapsulate(A, s, u, v, q)
    success = (ss_alice == ss_bob)  # Direct comparison for bytes
    
    # Debug: Print v and v_prime to inspect values
    print(f"v: {v}, v_prime: {v_prime}")

    # Encrypt and decrypt
    enc_key = encrypt(ss_alice, message.encode(), q)
    ciphertext = enc_key['ciphertext']
    decrypted = "Decryption failed (invalid UTF-8)"  # Default error message
    if success:
        try:
            decrypted = decrypt(ss_bob, ciphertext, q).decode('utf-8')
        except UnicodeDecodeError:
            decrypted = "Decryption failed (invalid UTF-8 sequence)"

    # Generate dynamic explanation with user inputs and calculations
    explanation_content = f"""
    <h2>How Lattice Cryptography Works with Your Numbers</h2>
<p>
Think of this like a 3D treasure hunt where you’re hiding a secret path from quantum computers!  
You chose <code>n={n}</code>, <code>q={q}</code>, and <code>noise scale={noise_scale}</code>.  
Here’s how it all comes together—step by step, just like assembling a puzzle with the diagrams!
</p>

<ol>
    <li><strong>Your Playground Size (<code>n={n}</code>)</strong><br>
    The lattice is a grid with <code>{n}</code> dimensions, like a 3D jungle gym of points.  
    Each direction is defined by a basis vector (B₁, B₂, B₃, …).  
    The diagram shows these stretching out to form your mathematical playground!</li>

    <li><strong>Your Secret Path (<code>s</code>)</strong><br>
    Your secret vector is <code>s = {s.flatten().tolist()}</code>, a list of <code>{n}</code> numbers.  
    It’s your hidden route through the lattice—marked as the “Clean Point” in the diagram.</li>

    <li><strong>The Public Map (<code>A</code>)</strong><br>
    You publish a matrix <code>A</code> of size <code>{n}×{n}</code>:  
    <pre>{np.array2string(A, separator=', ')}</pre>
    When you multiply it by your secret vector (<code>A @ s</code>), you get a clean lattice point.  
    The “Clean Point” in the visual corresponds to this product!</li>

    <li><strong>Wrapping Numbers (<code>q={q}</code>)</strong><br>
    Everything happens modulo <code>{q}</code>, which means numbers “wrap around” after hitting <code>{q}</code>.  
    It’s like a number clock that resets every <code>{q}</code> ticks.  
    So we compute <code>(A @ s) mod {q}</code> to keep all coordinates within range.</li>

    <li><strong>Adding Fog (Noise)</strong><br>
    We introduce a small random “noise” vector <code>e</code> drawn from a normal distribution:  
    <code>e = {np.random.normal(0, noise_scale, size=(n, 1)).flatten().tolist()}</code>  
    This noise, scaled by <code>{noise_scale}</code>, makes the result fuzzy—shown as the black arrow shifting the clean point to the “Noisy Point.”</li>

    <li><strong>Your Clue (<code>b</code>)</strong><br>
    Now we combine the clean point and noise:  
    <code>b = (A * s + e) mod {q} = {b.flatten().tolist()}</code>  
    This becomes your encrypted clue sent to Bob.  
    In the diagram, this is the noisy point floating near your secret!</li>

    <li><strong>Bob’s Map (<code>u</code>)</strong><br>
    Bob picks his own random vector <code>r</code> and computes:  
    <code>u = (Aᵀ * r + e₁) mod {q} = {u.flatten().tolist()}</code>  
    The chart labeled “Vector u” shows this as vertical bars—Bob’s version of your clue.</li>

    <li><strong>Alice’s Output (<code>v</code>)</strong><br>
    Using Bob’s <code>r</code>, Alice computes her shared value:  
    <code>v = (bᵀ * r + e₂) mod {q} = {v}</code>  
    This produces her half of the shared secret, visualized in the “v vs v” plot.</li>

    <li><strong>Bob’s Guess (<code>v′</code>)</strong><br>
    Bob uses his knowledge of <code>u</code> and your secret <code>s</code> to estimate:  
    <code>v′ = (uᵀ * s) mod {q} = {v_prime}</code>  
    The diagram compares <code>v</code> and <code>v′</code>—if they’re close, the secret matches despite the noise!</li>

    <li><strong>Shared Secret Codes</strong><br>
    Both sides derive cryptographic keys (<code>ss_alice</code> and <code>ss_bob</code>) from <code>u</code> and <code>v</code> (or <code>v′</code>).  
    If it says “<em>Success: Yes</em>,” that means their secrets align—the system works!</li>

    <li><strong>Locked Message (Ciphertext)</strong><br>
    Finally, Alice encrypts your message <code>'{message}'</code> into ciphertext:  
    <code>{ciphertext.hex()}</code>.  
    If Bob’s derived code matches, he decrypts it back to <code>'{decrypted}'</code>—your hidden treasure revealed!</li>
    </ol>

    <p>
    So this whole process is like a noisy treasure map:  
    quantum computers get lost in the fog, but Bob—using the right math—finds the path.  
    Try adjusting <code>n</code>, <code>q</code>, or <code>noise_scale</code> to see how the lattice shifts in your diagrams!
    </p>
    """

    # Plot lattice (increased size with corrected shapes)
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    clean_point = (A @ s).flatten()  # Ensure 1D array
    noisy_point = b.flatten()  # Ensure 1D array
    for i in range(n):
        basis_vec = A[:, i]  # 1D array (n,)
        # Use available dimensions, pad with 0 for 3D if n < 3
        x = basis_vec[0] if i < len(basis_vec) else 0
        y = basis_vec[1] if i < len(basis_vec) else 0
        z = basis_vec[2] if i < len(basis_vec) and len(basis_vec) > 2 else 0
        ax.quiver(0, 0, 0, x, y, z, color='b', label=f'Basis Vector {i+1}' if i == 0 else "")
        ax.text(x, y, z, f'B{i+1}', color='b')
    ax.scatter(clean_point[0], clean_point[1], clean_point[2] if len(clean_point) > 2 else 0, c='g', label='Clean Point (A@s)')
    ax.text(clean_point[0], clean_point[1], clean_point[2] if len(clean_point) > 2 else 0, 'Clean', color='g')
    ax.scatter(noisy_point[0], noisy_point[1], noisy_point[2] if len(noisy_point) > 2 else 0, c='r', label='Noisy Point (A@s+e)')
    ax.text(noisy_point[0], noisy_point[1], noisy_point[2] if len(noisy_point) > 2 else 0, 'Noisy', color='r')
    ax.plot([clean_point[0], noisy_point[0]], [clean_point[1], noisy_point[1]], [clean_point[2] if len(clean_point) > 2 else 0, noisy_point[2] if len(noisy_point) > 2 else 0], 'k--', label='Noise Vector')
    ax.text((clean_point[0] + noisy_point[0])/2, (clean_point[1] + noisy_point[1])/2, (clean_point[2] + noisy_point[2])/2 if len(clean_point) > 2 and len(noisy_point) > 2 else 0, 'Noise', color='k')
    ax.legend()
    plt.savefig('static/lattice.png')
    plt.close()

    # Plot handshake (increased size with annotations)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.text(0.1, 0.8, 'Bob', fontsize=14, bbox=dict(facecolor='lightblue'))
    ax.text(0.9, 0.8, 'Alice', fontsize=14, bbox=dict(facecolor='lightgreen'))
    ax.arrow(0.3, 0.7, 0.4, 0, head_width=0.05, head_length=0.05, fc='blue', ec='blue', label='PKI (b)')
    ax.text(0.5, 0.7, 'PKI', color='blue')
    ax.arrow(0.7, 0.5, -0.4, 0, head_width=0.05, head_length=0.05, fc='green', ec='green', label='(u, v)')
    ax.text(0.5, 0.5, '(u, v)', color='green')
    ax.arrow(0.3, 0.3, 0.4, 0, head_width=0.05, head_length=0.05, fc='red', ec='red', label='Ciphertext')
    ax.text(0.5, 0.3, 'Ciphertext', color='red')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.legend()
    plt.savefig('static/handshake.png')
    plt.close()

    # Plot cryptograph (increased size with annotations)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    ax1.bar(range(n), u.flatten(), label='u (Alice/Bob)', alpha=0.5)
    for i, val in enumerate(u.flatten()):
        ax1.text(i, val, f'u[{i}]', ha='center', va='bottom')
    ax1.set_title('Vector u', fontsize=12)
    ax1.legend()
    ax2.bar([0, 1], [v, v_prime], tick_label=['v (Alice)', "v' (Bob)"], alpha=0.5)
    ax2.text(0, v, f'v={v}', ha='center', va='bottom')
    ax2.text(1, v_prime, f"v'={v_prime}", ha='center', va='bottom')
    ax2.set_title('v vs v\' Comparison', fontsize=12)
    plt.savefig('static/cryptograph.png')
    plt.close()

    return render_template('index.html', n=n, q=q, noise_scale=noise_scale, message=message,
                           ss_alice=ss_alice.hex(), ss_bob=ss_bob.hex(),
                           success=success, ciphertext=ciphertext.hex(), decrypted=decrypted,
                           readme_content=readme_content, quantum_content=quantum_content, about_content=about_content, explanation_content=explanation_content)

if __name__ == '__main__':
    from waitress import serve
    serve(app,host='0.0.0.0',port=5000)