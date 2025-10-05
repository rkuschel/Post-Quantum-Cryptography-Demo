import numpy as np
import hashlib

def generate_keypair(n, q, noise_scale):
    A = np.random.randint(0, q, size=(n, n))
    s = np.random.randint(0, q, size=(n, 1))
    e = np.random.normal(0, noise_scale, size=(n, 1)).astype(int) % q
    b = (A @ s + e) % q
    return A, s, b

def encapsulate(A, b, q, noise_scale, r):
    e1 = np.random.normal(0, noise_scale, size=(A.shape[0], 1)).astype(int) % q
    e2 = int(np.random.normal(0, noise_scale)) % q
    u = (A.T @ r + e1) % q
    v = (b.T @ r + e2) % q
    v = v.item()  # Convert single-element array to scalar
    ss = hashlib.shake_256(u.tobytes() + np.array([v]).tobytes()).digest(16)
    return u, v, ss

def decapsulate(A, s, u, v, q):
    v_prime = (u.T @ s) % q
    v_prime = v_prime.item()  # Convert single-element array to scalar
    ss = hashlib.shake_256(u.tobytes() + np.array([v_prime]).tobytes()).digest(16)
    return v_prime, ss

def encrypt(ss, plaintext, q):
    enc_key = hashlib.shake_256(ss + b"key").digest(len(plaintext))
    ciphertext = bytes(a ^ b for a, b in zip(plaintext, enc_key))
    return {'enc_key': enc_key, 'ciphertext': ciphertext}

def decrypt(ss, ciphertext, q):
    enc_key = hashlib.shake_256(ss + b"key").digest(len(ciphertext))
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, enc_key))
    return plaintext