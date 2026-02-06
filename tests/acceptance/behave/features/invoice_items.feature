Feature: Invoice items management
  In order to bill correctly
  As an API client
  I want to add, update and remove invoice items

  Background: Given the API is available

  Scenario: Add an item to an invoice
    When I create an invoice with customer "Helen" and amount 0.0 and invoiceNumber "INV-010"
    And I add an item to the invoice with productId "P1" and description "Widget" and quantity 2 and unitPrice 10.0
    Then the API responds with items_count 1 and amount 20.0

  Scenario: Update item quantity while draft
    When I create an invoice with customer "Ivy" and amount 0.0 and invoiceNumber "INV-011"
    And I add an item to the invoice with productId "P2" and description "Gadget" and quantity 1 and unitPrice 5.0
    And I update item P2 on the invoice to quantity 3
    Then the API responds with items_count 1 and amount 15.0

  Scenario: Cannot update item after issuing
    When I create an invoice with customer "Jack" and amount 0.0 and invoiceNumber "INV-012"
    And I add an item to the invoice with productId "P3" and description "Thing" and quantity 1 and unitPrice 7.0
    And I issue the invoice
    And I update item P3 on the invoice to quantity 2
    Then the API response status code is 400

  Scenario: Delete item while draft
    When I create an invoice with customer "Karl" and amount 0.0 and invoiceNumber "INV-013"
    And I add an item to the invoice with productId "P4" and description "Stuff" and quantity 2 and unitPrice 3.0
    And I delete item P4 from the invoice
    Then the API responds with items_count 0 and amount 0.0

  Scenario: Cannot delete item after issuing
    When I create an invoice with customer "Liam" and amount 0.0 and invoiceNumber "INV-014"
    And I add an item to the invoice with productId "P5" and description "Object" and quantity 1 and unitPrice 9.0
    And I issue the invoice
    And I delete item P5 from the invoice
    Then the API response status code is 400
