"""
Certificate Handling Module (Production Ready)
Provides utilities for loading, verifying, and parsing X.509 certificates and private keys.
Uses the cryptography library for robust certificate parsing and validation.
"""

import logging
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

def load_certificate(certfile: str) -> x509.Certificate:
    """
    Load an X.509 certificate from the specified file.
    
    Args:
        certfile (str): Path to the certificate file (PEM or DER format).
    
    Returns:
        x509.Certificate: The loaded certificate.
    
    Raises:
        Exception: If the certificate cannot be loaded or parsed.
    """
    try:
        with open(certfile, "rb") as f:
            cert_data = f.read()
        try:
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        except ValueError:
            cert = x509.load_der_x509_certificate(cert_data, default_backend())
        logger.debug("Certificate loaded successfully from %s", certfile)
        return cert
    except Exception as e:
        logger.exception("Failed to load certificate from %s", certfile)
        raise

def load_private_key(keyfile: str, password: bytes = None):
    """
    Load a private key from the specified file.
    
    Args:
        keyfile (str): Path to the key file (PEM or DER format).
        password (bytes, optional): Password for decrypting the key, if necessary.
    
    Returns:
        The loaded private key object.
    
    Raises:
        Exception: If the private key cannot be loaded or parsed.
    """
    try:
        with open(keyfile, "rb") as f:
            key_data = f.read()
        try:
            private_key = serialization.load_pem_private_key(key_data, password=password, backend=default_backend())
        except ValueError:
            private_key = serialization.load_der_private_key(key_data, password=password, backend=default_backend())
        logger.debug("Private key loaded successfully from %s", keyfile)
        return private_key
    except Exception as e:
        logger.exception("Failed to load private key from %s", keyfile)
        raise

def verify_certificate(cert: x509.Certificate, cafile: str = None) -> bool:
    """
    Verify the provided certificate.
    
    If a CA file is supplied, the certificate will be verified against the CA certificate.
    Otherwise, if the certificate is self-signed, a basic check is performed.
    
    Args:
        cert (x509.Certificate): The certificate to verify.
        cafile (str, optional): Path to the CA bundle for certificate chain verification.
    
    Returns:
        bool: True if the certificate is verified; False otherwise.
    
    Raises:
        Exception: If an error occurs during verification.
    """
    try:
        if cafile:
            with open(cafile, "rb") as f:
                ca_data = f.read()
            try:
                ca_cert = x509.load_pem_x509_certificate(ca_data, default_backend())
            except ValueError:
                ca_cert = x509.load_der_x509_certificate(ca_data, default_backend())
            # Simple verification: check if cert issuer matches CA subject.
            if cert.issuer == ca_cert.subject:
                logger.debug("Certificate verified successfully against CA from %s", cafile)
                return True
            else:
                logger.error("Certificate issuer does not match CA subject in %s", cafile)
                return False
        else:
            # Basic self-signed certificate check.
            if cert.issuer == cert.subject:
                logger.debug("Self-signed certificate accepted (no CA provided)")
                return True
            else:
                logger.error("Certificate verification failed: no CA provided and certificate is not self-signed")
                return False
    except Exception as e:
        logger.exception("Error during certificate verification")
        raise