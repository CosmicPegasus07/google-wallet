# Google Wallet Agent Test Scenarios

## Database Overview

### Users:
- **Alice Johnson** (ID: 1) - alice@example.com
- **Bob Smith** (ID: 2) - bob@example.com  
- **Charlie Brown** (ID: 3) - charlie@example.com
- **Diana Prince** (ID: 4) - diana@example.com
- **Eve Wilson** (ID: 5) - eve@example.com

### Groups:
- **Family Trip** (ID: 1) - Members: Alice, Bob, Charlie
- **Office Lunch** (ID: 2) - Members: Bob, Diana, Eve
- **Roommates** (ID: 3) - Members: Charlie, Diana, Eve
- **Friends Dinner** (ID: 4) - Members: Alice, Bob, Diana

## Test Scenarios

### 1. Input Validation Tests

#### Test 1.1: Missing user_id
**Prompt:**
```
Split a $100 dinner bill equally among the Family Trip group.
```
**Expected:** Agent should ask for user_id

#### Test 1.2: Missing group_name
**Prompt:**
```
user_id: 1
Split a $100 dinner bill equally.
```
**Expected:** Agent should ask for group_name

#### Test 1.3: Invalid user_id
**Prompt:**
```
user_id: 999
group_name: Family Trip
Split a $100 dinner bill equally.
```
**Expected:** Error message about user not found

#### Test 1.4: User not in group
**Prompt:**
```
user_id: 5
group_name: Family Trip
Split a $100 dinner bill equally.
```
**Expected:** Error message about user not being a member of the group

### 2. Equal Split Tests

#### Test 2.1: Basic Equal Split
**Prompt:**
```
user_id: 1
group_name: Family Trip
Split a $150.00 hotel bill equally among all members.
```
**Expected Result:**
```json
{
    "group_name": "Family Trip",
    "split_type": "equal",
    "total_amount": 150.00,
    "split_summary": {
        "Alice Johnson": 50.00,
        "Bob Smith": 50.00,
        "Charlie Brown": 50.00
    }
}
```

#### Test 2.2: Equal Split with Rounding
**Prompt:**
```
user_id: 2
group_name: Office Lunch
Split a $100.00 lunch bill equally.
```
**Expected:** Should handle rounding properly for 3 members

### 3. Percentage Split Tests

#### Test 3.1: Custom Percentage Split
**Prompt:**
```
user_id: 1
group_name: Family Trip
Split a $300.00 vacation expense with these percentages:
- Alice Johnson: 50%
- Bob Smith: 30%
- Charlie Brown: 20%
```
**Expected Result:**
```json
{
    "group_name": "Family Trip",
    "split_type": "percentage",
    "total_amount": 300.00,
    "split_summary": {
        "Alice Johnson": 150.00,
        "Bob Smith": 90.00,
        "Charlie Brown": 60.00
    }
}
```

### 4. Custom Amount Split Tests

#### Test 4.1: Custom Amount Split
**Prompt:**
```
user_id: 3
group_name: Roommates
Split a $200.00 utility bill with custom amounts:
- Charlie Brown: $80.00
- Diana Prince: $70.00
- Eve Wilson: $50.00
```
**Expected:** Should validate amounts sum to total

### 5. Itemized Split Tests

#### Test 5.1: Itemized Split
**Prompt:**
```
user_id: 1
group_name: Friends Dinner
Split this restaurant bill itemized:
- Pizza ($30.00): Alice Johnson, Bob Smith
- Salad ($15.00): Diana Prince
- Drinks ($25.00): All members equally
Total: $70.00
```
**Expected:** Should split pizza between Alice and Bob, salad to Diana, drinks equally

### 6. Group Information Tests

#### Test 6.1: Get Group Information
**Prompt:**
```
user_id: 1
group_name: Family Trip
Show me information about this group.
```
**Expected:** Should return group details and member list

#### Test 6.2: Get User Groups
**Prompt:**
```
user_id: 1
Show me all groups I belong to.
```
**Expected:** Should return Family Trip and Friends Dinner groups

#### Test 6.3: Get Group Balances
**Prompt:**
```
user_id: 1
group_name: Family Trip
Show me the current balances for this group.
```
**Expected:** Should show who owes what based on existing expenses

### 7. Complex Scenarios

#### Test 7.1: Multi-step Interaction
**Prompt:**
```
user_id: 2
group_name: Office Lunch
I need to split a $120.00 team lunch bill. First show me who's in this group, then split it equally.
```
**Expected:** Should first show group members, then perform equal split

#### Test 7.2: Receipt Processing
**Prompt:**
```
user_id: 1
group_name: Family Trip
Process this receipt:
{
    "total": 85.50,
    "items": [
        {"name": "Appetizer", "price": 25.50},
        {"name": "Main Course 1", "price": 30.00},
        {"name": "Main Course 2", "price": 30.00}
    ],
    "location": "Italian Restaurant",
    "date": "2024-01-26"
}
Split equally among all members.
```
**Expected:** Should process receipt and split $85.50 equally

## Quick Test Commands

### Test Agent Response (Python)
```python
# Test the agent directly
from group_splitting_agent.agent import root_agent

# Test equal split
response = root_agent.run("user_id: 1, group_name: Family Trip, Split $150 hotel bill equally")
print(response)
```

### Test Individual Tools
```python
from group_splitting_agent.tools.agent_tools import *

# Test group info
print(get_group_info("Family Trip", 1))

# Test equal split
print(split_bill_equal(1, "Family Trip", 150.00, "Hotel bill"))

# Test user groups
print(get_user_groups_info(1))
```

## Expected Behaviors

1. **Always validate inputs** - user_id and group_name must be provided
2. **Handle errors gracefully** - Return JSON with error messages
3. **Accurate calculations** - All splits should sum to total amount
4. **Proper formatting** - Results in specified JSON format
5. **Database integration** - Use real group and user data
6. **Tool utilization** - Use appropriate tools for different operations

## Success Criteria

- ✅ Agent validates user_id and group_name before processing
- ✅ All splitting methods work correctly (equal, percentage, custom, itemized)
- ✅ Error handling for invalid inputs
- ✅ Database queries return accurate information
- ✅ JSON output format is consistent
- ✅ Calculations are mathematically correct
- ✅ Agent uses appropriate tools for different tasks
