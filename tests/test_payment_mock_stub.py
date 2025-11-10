"""
Test Suite for Payment Functions - Assignment 3
Tests pay_late_fees() and refund_late_fee_payment() using mocking and stubbing
"""

import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway


# ========================================================================================
# TEST SUITE FOR pay_late_fees()
# ========================================================================================

def test_pay_late_fees_successful_payment(mocker):
    """
    Test successful payment processing for late fees.
    Stubs: calculate_late_fee_for_book, get_book_by_id
    Mocks: payment_gateway.process_payment
    Verification: assert_called_once_with() to verify correct parameters
    """
    # Stub database functions with fake data
    mocker.patch('services.library_service.calculate_late_fee_for_book', 
                 return_value={
                     'fee_amount': 5.00,
                     'days_overdue': 10,
                     'status': 'Overdue'
                 })
    mocker.patch('services.library_service.get_book_by_id',
                 return_value={
                     'id': 1,
                     'title': 'The Great Gatsby',
                     'author': 'F. Scott Fitzgerald'
                 })
    
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_12345", "Payment successful")
    
    # Execute the function
    success, message, txn_id = pay_late_fees("123456", 1, mock_gateway)
    
    # Assertions
    assert success == True
    assert "Payment successful" in message
    assert txn_id == "txn_12345"
    
    # Verify mock was called with correct parameters
    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=5.00,
        description="Late fees for 'The Great Gatsby'"
    )


def test_pay_late_fees_payment_declined(mocker):
    """
    Test payment declined by payment gateway.
    Stubs: calculate_late_fee_for_book, get_book_by_id
    Mocks: payment_gateway.process_payment (returns failure)
    Verification: assert_called_once() to verify gateway was called
    """
    # Stub database functions
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={
                     'fee_amount': 7.50,
                     'days_overdue': 15,
                     'status': 'Overdue'
                 })
    mocker.patch('services.library_service.get_book_by_id',
                 return_value={
                     'id': 2,
                     'title': '1984',
                     'author': 'George Orwell'
                 })
    
    # Mock payment gateway to return failure
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, None, "Insufficient funds")
    
    # Execute
    success, message, txn_id = pay_late_fees("234567", 2, mock_gateway)
    
    # Assertions
    assert success == False
    assert "Payment failed" in message
    assert txn_id is None
    
    # Verify mock was called
    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fees_invalid_patron_id(mocker):
    """
    Test with invalid patron ID - should reject before calling payment gateway.
    Mocks: payment_gateway
    Verification: assert_not_called() to ensure gateway was NOT called
    """
    # Mock payment gateway (should never be called)
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Test various invalid patron IDs
    invalid_ids = ["12345", "1234567", "abc123", "", None, "12-3456"]
    
    for invalid_id in invalid_ids:
        success, message, txn_id = pay_late_fees(invalid_id, 1, mock_gateway)
        
        # Assertions
        assert success == False
        assert "Invalid patron ID" in message
        assert txn_id is None
    
    # Verify payment gateway was never called
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_late_fees(mocker):
    """
    Test when patron has no late fees - should not process payment.
    Stubs: calculate_late_fee_for_book (returns 0)
    Mocks: payment_gateway
    Verification: assert_not_called() to ensure no payment was attempted
    """
    # Stub to return zero fees
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={
                     'fee_amount': 0.00,
                     'days_overdue': 0,
                     'status': 'On time'
                 })
    
    # Mock payment gateway (should not be called)
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute
    success, message, txn_id = pay_late_fees("345678", 3, mock_gateway)
    
    # Assertions
    assert success == False
    assert "No late fees" in message
    assert txn_id is None
    
    # Verify payment gateway was NOT called
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_network_error_exception(mocker):
    """
    Test handling of network errors from payment gateway.
    Stubs: calculate_late_fee_for_book, get_book_by_id
    Mocks: payment_gateway.process_payment (raises exception)
    Verification: Proper exception handling
    """
    # Stub database functions
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={
                     'fee_amount': 3.50,
                     'days_overdue': 7,
                     'status': 'Overdue'
                 })
    mocker.patch('services.library_service.get_book_by_id',
                 return_value={
                     'id': 4,
                     'title': 'To Kill a Mockingbird',
                     'author': 'Harper Lee'
                 })
    
    # Mock payment gateway to raise exception
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network timeout")
    
    # Execute
    success, message, txn_id = pay_late_fees("456789", 4, mock_gateway)
    
    # Assertions
    assert success == False
    assert "Payment processing error" in message
    assert "Network timeout" in message
    assert txn_id is None
    
    # Verify mock was called
    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fees_book_not_found(mocker):
    """
    Test when book ID doesn't exist in database.
    Stubs: calculate_late_fee_for_book, get_book_by_id (returns None)
    Mocks: payment_gateway
    Verification: assert_not_called() - should fail before calling gateway
    """
    # Stub database functions
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={
                     'fee_amount': 5.00,
                     'days_overdue': 10,
                     'status': 'Overdue'
                 })
    mocker.patch('services.library_service.get_book_by_id',
                 return_value=None)  # Book not found
    
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute
    success, message, txn_id = pay_late_fees("567890", 999, mock_gateway)
    
    # Assertions
    assert success == False
    assert "Book not found" in message
    assert txn_id is None
    
    # Verify payment gateway was NOT called
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_invalid_fee_calculation(mocker):
    """
    Test when calculate_late_fee_for_book returns invalid data.
    Stubs: calculate_late_fee_for_book (returns None)
    Mocks: payment_gateway
    Verification: assert_not_called()
    """
    # Stub to return invalid data
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value=None)
    
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute
    success, message, txn_id = pay_late_fees("678901", 5, mock_gateway)
    
    # Assertions
    assert success == False
    assert "Unable to calculate late fees" in message
    assert txn_id is None
    
    # Verify payment gateway was NOT called
    mock_gateway.process_payment.assert_not_called()


# ========================================================================================
# TEST SUITE FOR refund_late_fee_payment()
# ========================================================================================

def test_refund_late_fee_successful(mocker):
    """
    Test successful refund processing.
    Mocks: payment_gateway.refund_payment
    Verification: assert_called_once_with() to verify correct parameters
    """
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund processed successfully")
    
    # Execute
    success, message = refund_late_fee_payment("txn_12345", 5.00, mock_gateway)
    
    # Assertions
    assert success == True
    assert "Refund processed successfully" in message
    
    # Verify mock was called with correct parameters
    mock_gateway.refund_payment.assert_called_once_with("txn_12345", 5.00)


def test_refund_late_fee_invalid_transaction_id(mocker):
    """
    Test refund with invalid transaction ID (doesn't start with 'txn_').
    Mocks: payment_gateway
    Verification: assert_not_called() - should reject before calling gateway
    """
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Test various invalid transaction IDs
    invalid_txn_ids = ["12345", "abc_12345", "", None, "TXN_12345", "payment_123"]
    
    for invalid_txn in invalid_txn_ids:
        success, message = refund_late_fee_payment(invalid_txn, 5.00, mock_gateway)
        
        # Assertions
        assert success == False
        assert "Invalid transaction ID" in message
    
    # Verify payment gateway was never called
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_negative_amount(mocker):
    """
    Test refund with negative amount - should be rejected.
    Mocks: payment_gateway
    Verification: assert_not_called()
    """
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute with negative amount
    success, message = refund_late_fee_payment("txn_12345", -5.00, mock_gateway)
    
    # Assertions
    assert success == False
    assert "must be greater than 0" in message
    
    # Verify payment gateway was NOT called
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_zero_amount(mocker):
    """
    Test refund with zero amount - should be rejected.
    Mocks: payment_gateway
    Verification: assert_not_called()
    """
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute with zero amount
    success, message = refund_late_fee_payment("txn_67890", 0.00, mock_gateway)
    
    # Assertions
    assert success == False
    assert "must be greater than 0" in message
    
    # Verify payment gateway was NOT called
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_exceeds_maximum(mocker):
    """
    Test refund with amount exceeding $15 maximum late fee cap.
    Mocks: payment_gateway
    Verification: assert_not_called()
    """
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Test amounts exceeding $15
    excessive_amounts = [15.01, 20.00, 100.00, 15.50]
    
    for amount in excessive_amounts:
        success, message = refund_late_fee_payment("txn_99999", amount, mock_gateway)
        
        # Assertions
        assert success == False
        assert "exceeds maximum late fee" in message
    
    # Verify payment gateway was never called
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_gateway_failure(mocker):
    """
    Test when payment gateway returns failure status.
    Mocks: payment_gateway.refund_payment (returns False)
    Verification: assert_called_once()
    """
    # Mock payment gateway to return failure
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Transaction already refunded")
    
    # Execute
    success, message = refund_late_fee_payment("txn_11111", 10.00, mock_gateway)
    
    # Assertions
    assert success == False
    assert "Refund failed" in message
    assert "Transaction already refunded" in message
    
    # Verify mock was called
    mock_gateway.refund_payment.assert_called_once()


def test_refund_late_fee_exception_handling(mocker):
    """
    Test exception handling during refund processing.
    Mocks: payment_gateway.refund_payment (raises exception)
    Verification: Proper exception handling
    """
    # Mock payment gateway to raise exception
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.side_effect = Exception("Database connection lost")
    
    # Execute
    success, message = refund_late_fee_payment("txn_22222", 8.50, mock_gateway)
    
    # Assertions
    assert success == False
    assert "Refund processing error" in message
    assert "Database connection lost" in message
    
    # Verify mock was called
    mock_gateway.refund_payment.assert_called_once()


def test_refund_late_fee_maximum_valid_amount(mocker):
    """
    Test refund with exactly $15.00 (maximum valid amount).
    Mocks: payment_gateway.refund_payment
    Verification: assert_called_once_with()
    """
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund successful")
    
    # Execute with maximum valid amount
    success, message = refund_late_fee_payment("txn_33333", 15.00, mock_gateway)
    
    # Assertions
    assert success == True
    assert "Refund" in message
    
    # Verify correct amount was passed
    mock_gateway.refund_payment.assert_called_once_with("txn_33333", 15.00)


# ========================================================================================
# EDGE CASE TESTS
# ========================================================================================

def test_pay_late_fees_with_default_gateway(mocker):
    """
    Test pay_late_fees when no payment_gateway is provided (uses default).
    This tests the None check and default gateway instantiation.
    """
    # Stub database functions
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={
                     'fee_amount': 2.50,
                     'days_overdue': 5,
                     'status': 'Overdue'
                 })
    mocker.patch('services.library_service.get_book_by_id',
                 return_value={
                     'id': 6,
                     'title': 'Pride and Prejudice',
                     'author': 'Jane Austen'
                 })
    
    # Mock the PaymentGateway class constructor
    mock_gateway_instance = Mock(spec=PaymentGateway)
    mock_gateway_instance.process_payment.return_value = (True, "txn_default", "Success")
    mocker.patch('services.library_service.PaymentGateway', return_value=mock_gateway_instance)
    
    # Execute without providing payment_gateway
    success, message, txn_id = pay_late_fees("789012", 6, None)
    
    # Assertions
    assert success == True
    assert txn_id == "txn_default"


def test_refund_late_fee_with_default_gateway(mocker):
    """
    Test refund_late_fee_payment when no payment_gateway is provided (uses default).
    """
    # Mock the PaymentGateway class constructor
    mock_gateway_instance = Mock(spec=PaymentGateway)
    mock_gateway_instance.refund_payment.return_value = (True, "Refund successful")
    mocker.patch('services.library_service.PaymentGateway', return_value=mock_gateway_instance)
    
    # Execute without providing payment_gateway
    success, message = refund_late_fee_payment("txn_44444", 7.25, None)
    
    # Assertions
    assert success == True
    assert "Refund" in message
