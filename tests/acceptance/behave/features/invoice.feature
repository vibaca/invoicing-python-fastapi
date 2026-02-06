Feature: Invoice creation
  In order to bill customers
  As an API client
  I want to create invoices via REST

  Scenario: Create an invoice
    Given the API is available
    When I create an invoice with customer "Alice" and amount 100.0 and invoiceNumber "INV-001"
    Then the API responds with a created invoice id
