Feature: Invoice state transitions
  In order to manage invoice lifecycle
  As an API client
  I want to issue, pay and cancel invoices

  Background: Given the API is available

  Scenario: Issue an invoice
    When I create an invoice with customer "Charlie" and amount 75.0 and invoiceNumber "INV-003"
    And I issue the invoice
    Then the API responds with status "issued"

  Scenario: Pay an issued invoice
    When I create an invoice with customer "Dana" and amount 80.0 and invoiceNumber "INV-004"
    And I issue the invoice
    And I pay the invoice
    Then the API responds with status "paid"

  Scenario: Cannot pay a draft invoice
    When I create an invoice with customer "Eve" and amount 90.0 and invoiceNumber "INV-005"
    And I pay the invoice
    Then the API response status code is 404

  Scenario: Cancel a draft invoice
    When I create an invoice with customer "Frank" and amount 20.0 and invoiceNumber "INV-006"
    And I cancel the invoice
    Then the API responds with status "cancelled"

  Scenario: Cancel an issued invoice
    When I create an invoice with customer "Gina" and amount 30.0 and invoiceNumber "INV-007"
    And I issue the invoice
    And I cancel the invoice
    Then the API responds with status "cancelled"
