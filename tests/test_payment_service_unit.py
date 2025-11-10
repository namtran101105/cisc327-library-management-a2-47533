"""
Unit tests for PaymentGateway class (testing the actual implementation)
Note: In production, this would be an external service we wouldn't test.
"""
import pytest
from services.payment_service import PaymentGateway


def test_process_payment_success():
    """Test successful payment processing"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("123456", 5.00, "Late fees")
    
    assert success is True
    assert txn_id == "txn_123456_500"
    assert "success" in message.lower()


def test_process_payment_invalid_patron_id_too_short():
    """Test payment with invalid patron ID (too short)"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("12345", 5.00, "Late fees")
    
    assert success is False
    assert txn_id is None
    assert "invalid patron id" in message.lower()


def test_process_payment_invalid_patron_id_too_long():
    """Test payment with invalid patron ID (too long)"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("1234567", 5.00, "Late fees")
    
    assert success is False
    assert txn_id is None


def test_process_payment_invalid_patron_id_empty():
    """Test payment with empty patron ID"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("", 5.00, "Late fees")
    
    assert success is False
    assert txn_id is None


def test_process_payment_zero_amount():
    """Test payment with zero amount"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("123456", 0.00, "Late fees")
    
    assert success is False
    assert txn_id is None
    assert "invalid amount" in message.lower()


def test_process_payment_negative_amount():
    """Test payment with negative amount"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("123456", -5.00, "Late fees")
    
    assert success is False
    assert txn_id is None


def test_refund_payment_success():
    """Test successful refund"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("txn_123456_500", 5.00)
    
    assert success is True
    assert "Refund of $5.00" in message


def test_refund_payment_invalid_transaction_id():
    """Test refund with invalid transaction ID format"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("invalid_id", 5.00)
    
    assert success is False
    assert "invalid transaction id" in message.lower()


def test_refund_payment_empty_transaction_id():
    """Test refund with empty transaction ID"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("", 5.00)
    
    assert success is False


def test_refund_payment_zero_amount():
    """Test refund with zero amount"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("txn_123456_500", 0.00)
    
    assert success is False
    assert "invalid" in message.lower()


def test_refund_payment_negative_amount():
    """Test refund with negative amount"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("txn_123456_500", -5.00)
    
    assert success is False


def test_refund_payment_exceeds_maximum():
    """Test refund amount exceeding max late fee"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("txn_123456_500", 20.00)
    
    assert success is False
    assert "exceeds maximum" in message.lower()


def test_refund_payment_at_maximum_valid():
    """Test refund at exactly maximum valid amount"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("txn_123456_500", 15.00)
    
    assert success is True
    assert "Refund of $15.00" in message
