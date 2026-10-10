"""
Part 2 of 200 Question Bank:
Concepts D07, D08, D09, D10, D11, D12 (66 questions total, 11 per concept)
"""

QUESTIONS_PART2 = [
    # ==========================================
    # D07: Relational Algebra (11 questions)
    # ==========================================
    {
        "id": "Q_D07_A_01",
        "concept": "D07",
        "family": "A",
        "difficulty": 1,
        "prompt": "Which fundamental relational algebra operator filters rows based on a specified predicate condition?",
        "options": [
            {"id": "a", "text": "Selection (σ)", "correct": True},
            {"id": "b", "text": "Projection (π)", "correct": False, "maps_to": "D07", "misconception": "Projection filters columns (attributes), not rows"},
            {"id": "c", "text": "Cartesian Product (×)", "correct": False, "maps_to": "D07", "misconception": "Cartesian Product combines all pairs of tuples across two relations"},
            {"id": "d", "text": "Rename (ρ)", "correct": False, "maps_to": "D07", "misconception": "Rename changes relation or attribute identifiers"}
        ],
        "explanation": "Selection (σ) selects tuples that satisfy a given predicate condition, filtering horizontally.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_A_02",
        "concept": "D07",
        "family": "A",
        "difficulty": 1,
        "prompt": "Which relational algebra operator selects specific columns and removes duplicate rows from the result?",
        "options": [
            {"id": "a", "text": "Projection (π)", "correct": True},
            {"id": "b", "text": "Selection (σ)", "correct": False, "maps_to": "D07", "misconception": "Selection filters rows based on predicates, not columns"},
            {"id": "c", "text": "Intersection (∩)", "correct": False, "maps_to": "D07", "misconception": "Intersection finds common tuples across two relations"},
            {"id": "d", "text": "Natural Join (⋈)", "correct": False, "maps_to": "D07", "misconception": "Natural join combines tables based on matching common attributes"}
        ],
        "explanation": "Projection (π) extracts specified attributes (columns) and eliminates duplicates to maintain set semantics.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_A_03",
        "concept": "D07",
        "family": "A",
        "difficulty": 2,
        "prompt": "If relation R has 10 tuples and relation S has 20 tuples, how many tuples are in the Cartesian Product R × S?",
        "options": [
            {"id": "a", "text": "200 tuples", "correct": True},
            {"id": "b", "text": "30 tuples", "correct": False, "maps_to": "D07", "misconception": "Adds tuples instead of multiplying for Cartesian product"},
            {"id": "c", "text": "10 tuples", "correct": False, "maps_to": "D07", "misconception": "Takes minimum cardinality instead of multiplying"},
            {"id": "d", "text": "20 tuples", "correct": False, "maps_to": "D07", "misconception": "Takes maximum cardinality instead of multiplying"}
        ],
        "explanation": "The Cartesian product of two relations with cardinalities m and n produces exactly m × n tuples (10 × 20 = 200).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_A_04",
        "concept": "D07",
        "family": "A",
        "difficulty": 2,
        "prompt": "What condition must two relations R and S satisfy to be Union-Compatible in relational algebra?",
        "options": [
            {"id": "a", "text": "They must have the same degree (number of attributes) and corresponding attributes must share compatible domains", "correct": True},
            {"id": "b", "text": "They must have identical table names and primary keys", "correct": False, "maps_to": "D07", "misconception": "Union compatibility does not require identical names or primary keys"},
            {"id": "c", "text": "They must have the exact same number of tuples", "correct": False, "maps_to": "D07", "misconception": "Row count has no bearing on union compatibility"},
            {"id": "d", "text": "One relation must be a foreign key reference to the other", "correct": False, "maps_to": "D04", "misconception": "Confuses set operators with referential constraints"}
        ],
        "explanation": "Union compatibility requires two relations to have the same arity (degree) and pairwise compatible attribute domains.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_A_05",
        "concept": "D07",
        "family": "A",
        "difficulty": 3,
        "prompt": "Which relational algebra operator is specifically designed for queries involving universal quantification ('find students who took ALL required courses')?",
        "options": [
            {"id": "a", "text": "Division (÷)", "correct": True},
            {"id": "b", "text": "Difference (−)", "correct": False, "maps_to": "D07", "misconception": "Difference subtracts tuples; division captures 'for all' conditions"},
            {"id": "c", "text": "Theta Join (⋈_θ)", "correct": False, "maps_to": "D07", "misconception": "Theta join matches tuples based on a condition, not universal quantification"},
            {"id": "d", "text": "Intersection (∩)", "correct": False, "maps_to": "D07", "misconception": "Intersection finds common rows between two relations"}
        ],
        "explanation": "Relational division (R ÷ S) produces tuples in R that match with all tuples in S, modeling 'contains all' queries.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_A_06",
        "concept": "D07",
        "family": "A",
        "difficulty": 2,
        "prompt": "How does a Natural Join (R ⋈ S) differ from a Cartesian Product (R × S)?",
        "options": [
            {"id": "a", "text": "Natural join automatically equates identically named attributes and projects out the redundant duplicate columns", "correct": True},
            {"id": "b", "text": "Natural join only works on single-column tables", "correct": False, "maps_to": "D07", "misconception": "Natural join works on relations of any degree"},
            {"id": "c", "text": "Cartesian product eliminates all duplicate rows while Natural Join preserves all duplicates", "correct": False, "maps_to": "D07", "misconception": "Both adhere to relational set theory without duplicates"},
            {"id": "d", "text": "Natural join requires that both tables have identical cardinality", "correct": False, "maps_to": "D07", "misconception": "No requirement for identical row counts exists"}
        ],
        "explanation": "Natural join pairs tuples where attributes with matching names are equal, keeping only one copy of each common attribute.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_B_01",
        "concept": "D07",
        "family": "B",
        "difficulty": 1,
        "prompt": "If relation R(A, B, C) has degree 3 and relation S(D, E) has degree 2, what is the degree of R × S?",
        "options": [
            {"id": "a", "text": "5", "correct": True},
            {"id": "b", "text": "6", "correct": False, "maps_to": "D07", "misconception": "Multiplies degrees instead of summing column counts"},
            {"id": "c", "text": "3", "correct": False, "maps_to": "D07", "misconception": "Takes maximum degree instead of summing"},
            {"id": "d", "text": "2", "correct": False, "maps_to": "D07", "misconception": "Takes minimum degree instead of summing"}
        ],
        "explanation": "The degree (number of columns) of a Cartesian product is the sum of degrees of the operands: 3 + 2 = 5.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_B_02",
        "concept": "D07",
        "family": "B",
        "difficulty": 2,
        "prompt": "What is the result of the Set Difference operation R − S?",
        "options": [
            {"id": "a", "text": "A relation containing all tuples that belong to R but do not belong to S", "correct": True},
            {"id": "b", "text": "A relation containing tuples that belong to both R and S", "correct": False, "maps_to": "D07", "misconception": "Describes Intersection (R ∩ S) instead of Set Difference"},
            {"id": "c", "text": "A relation containing all tuples from both R and S combined", "correct": False, "maps_to": "D07", "misconception": "Describes Union (R ∪ S) instead of Set Difference"},
            {"id": "d", "text": "A relation containing tuples that belong to S but not R", "correct": False, "maps_to": "D07", "misconception": "Describes S − R (set difference is non-commutative)"}
        ],
        "explanation": "R − S yields tuples present in R that do not appear in S. Note that set difference is not commutative.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_B_03",
        "concept": "D07",
        "family": "B",
        "difficulty": 2,
        "prompt": "In relational algebra, what is the purpose of the Rename operator (ρ)?",
        "options": [
            {"id": "a", "text": "To rename relation schemas or attribute names to avoid ambiguity, especially in self-joins", "correct": True},
            {"id": "b", "text": "To permanently alter physical disk file filenames", "correct": False, "maps_to": "D01", "misconception": "Confuses relational algebra expressions with OS filesystem commands"},
            {"id": "c", "text": "To delete an attribute from a relation", "correct": False, "maps_to": "D07", "misconception": "Projection excludes attributes; Rename merely assigns new names"},
            {"id": "d", "text": "To convert numeric values into strings", "correct": False, "maps_to": "D02", "misconception": "Confuses schema renaming with data type conversion"}
        ],
        "explanation": "The Rename operator ρ_S(B1, B2, ...)(R) allows naming intermediate results and resolving duplicate column names.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_B_04",
        "concept": "D07",
        "family": "B",
        "difficulty": 3,
        "prompt": "Can Set Intersection (R ∩ S) be expressed using only the basic relational algebra operators {σ, π, ρ, ∪, −, ×}?",
        "options": [
            {"id": "a", "text": "Yes, R ∩ S can be rewritten as R − (R − S)", "correct": True},
            {"id": "b", "text": "No, Intersection is a primitive operator that cannot be derived", "correct": False, "maps_to": "D07", "misconception": "Intersection is a derived operator, not one of the primitive 5 operators"},
            {"id": "c", "text": "Only if R and S have degree 1", "correct": False, "maps_to": "D07", "misconception": "Derivation holds for any union-compatible relations of any degree"},
            {"id": "d", "text": "Only if R is a subset of S", "correct": False, "maps_to": "D07", "misconception": "Equivalence holds generally for all union-compatible sets"}
        ],
        "explanation": "Set intersection is a derived operator: R ∩ S ≡ R − (R − S). The fundamental 5 operators are σ, π, ∪, −, and ×.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D07_B_05",
        "concept": "D07",
        "family": "B",
        "difficulty": 1,
        "prompt": "What does a Theta Join (R ⋈_θ S) represent in relational algebra?",
        "options": [
            {"id": "a", "text": "A Cartesian Product followed by a Selection condition θ: σ_θ(R × S)", "correct": True},
            {"id": "b", "text": "A Projection followed by a Set Difference", "correct": False, "maps_to": "D07", "misconception": "Confuses join composition with projection and difference"},
            {"id": "c", "text": "A union of all non-matching tuples", "correct": False, "maps_to": "D09", "misconception": "Describes outer joins rather than theta join"},
            {"id": "d", "text": "A Division operation on common attributes", "correct": False, "maps_to": "D07", "misconception": "Theta join is not division"}
        ],
        "explanation": "A Theta Join (R ⋈_θ S) is formally defined as the selection σ_θ applied to the Cartesian product R × S.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D08: SQL Basics (11 questions)
    # ==========================================
    {
        "id": "Q_D08_A_01",
        "concept": "D08",
        "family": "A",
        "difficulty": 1,
        "prompt": "Which SQL clause is used to eliminate duplicate rows from query results?",
        "options": [
            {"id": "a", "text": "DISTINCT", "correct": True},
            {"id": "b", "text": "UNIQUE", "correct": False, "maps_to": "D04", "misconception": "UNIQUE is a table constraint keyword, DISTINCT is the query result modifier"},
            {"id": "c", "text": "GROUP BY", "correct": False, "maps_to": "D10", "misconception": "GROUP BY aggregates rows; DISTINCT specifically eliminates duplicates from projection"},
            {"id": "d", "text": "ORDER BY", "correct": False, "maps_to": "D08", "misconception": "ORDER BY sorts rows, it does not remove duplicates"}
        ],
        "explanation": "SELECT DISTINCT removes duplicate rows from the query output.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_A_02",
        "concept": "D08",
        "family": "A",
        "difficulty": 2,
        "prompt": "Consider the query: SELECT * FROM Employees WHERE bonus = NULL. What will this query return?",
        "options": [
            {"id": "a", "text": "Empty result set (zero rows), because comparison with NULL using '=' evaluates to UNKNOWN", "correct": True},
            {"id": "b", "text": "All rows where bonus is NULL", "correct": False, "maps_to": "D08", "misconception": "Assumes = NULL checks for null values instead of IS NULL"},
            {"id": "c", "text": "All rows where bonus is 0", "correct": False, "maps_to": "D08", "misconception": "Treats NULL as numeric zero"},
            {"id": "d", "text": "A SQL syntax compilation error", "correct": False, "maps_to": "D08", "misconception": "Syntax is valid SQL, but the predicate evaluates to UNKNOWN for every row"}
        ],
        "explanation": "In SQL, comparing anything with NULL using = returns UNKNOWN, which the WHERE clause filters out. To test for NULL, one must use IS NULL.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_A_03",
        "concept": "D08",
        "family": "A",
        "difficulty": 2,
        "prompt": "In SQL pattern matching using the LIKE operator, what does the underscore '_' symbol represent?",
        "options": [
            {"id": "a", "text": "Exactly one single character", "correct": True},
            {"id": "b", "text": "Zero or more characters", "correct": False, "maps_to": "D08", "misconception": "The percent '%' symbol represents zero or more characters"},
            {"id": "c", "text": "A literal underscore character", "correct": False, "maps_to": "D08", "misconception": "An underscore is a wildcard unless escaped"},
            {"id": "d", "text": "Any numeric digit from 0 to 9", "correct": False, "maps_to": "D08", "misconception": "Underscore matches any single character, not just digits"}
        ],
        "explanation": "In standard SQL LIKE patterns, '_' matches exactly one character, while '%' matches zero or more characters.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_A_04",
        "concept": "D08",
        "family": "A",
        "difficulty": 1,
        "prompt": "What is the default sort direction of the ORDER BY clause when ASC or DESC is not specified?",
        "options": [
            {"id": "a", "text": "Ascending (ASC)", "correct": True},
            {"id": "b", "text": "Descending (DESC)", "correct": False, "maps_to": "D08", "misconception": "Assumes descending order is the default"},
            {"id": "c", "text": "Randomized order", "correct": False, "maps_to": "D08", "misconception": "ORDER BY is deterministic sorting, not random"},
            {"id": "d", "text": "Insertion timestamp order", "correct": False, "maps_to": "D08", "misconception": "ORDER BY sorts values in the specified column, not insertion time"}
        ],
        "explanation": "ORDER BY defaults to ascending order (ASC) if no direction is specified.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_A_05",
        "concept": "D08",
        "family": "A",
        "difficulty": 3,
        "prompt": "Evaluate the condition: WHERE score BETWEEN 70 AND 90. Is a student with score = 70 included in the output?",
        "options": [
            {"id": "a", "text": "Yes, because the SQL BETWEEN operator is inclusive of both boundary values", "correct": True},
            {"id": "b", "text": "No, because BETWEEN is strictly exclusive (score > 70 AND score < 90)", "correct": False, "maps_to": "D08", "misconception": "Assumes BETWEEN is exclusive like Python range"},
            {"id": "c", "text": "Only if score is an integer", "correct": False, "maps_to": "D08", "misconception": "BETWEEN works inclusively for all comparable types"},
            {"id": "d", "text": "Only if 90 is also present in the table", "correct": False, "maps_to": "D08", "misconception": "Boundary inclusion does not require both values to exist"}
        ],
        "explanation": "In SQL, BETWEEN is inclusive: 'val BETWEEN low AND high' is equivalent to 'val >= low AND val <= high'.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_A_06",
        "concept": "D08",
        "family": "A",
        "difficulty": 2,
        "prompt": "What does a SQL CASE WHEN expression return if no WHEN condition is matched and there is no ELSE clause?",
        "options": [
            {"id": "a", "text": "NULL", "correct": True},
            {"id": "b", "text": "0", "correct": False, "maps_to": "D08", "misconception": "Assumes default fallback is numeric zero"},
            {"id": "c", "text": "Empty string ''", "correct": False, "maps_to": "D08", "misconception": "Assumes default fallback is empty string"},
            {"id": "d", "text": "A runtime exception", "correct": False, "maps_to": "D08", "misconception": "CASE expressions safely return NULL when no branch matches and ELSE is absent"}
        ],
        "explanation": "According to the SQL standard, if no WHEN clause matches and no ELSE clause is provided, the CASE expression returns NULL.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_B_01",
        "concept": "D08",
        "family": "B",
        "difficulty": 1,
        "prompt": "Which query correctly retrieves all customers whose email address is unknown or not recorded?",
        "options": [
            {"id": "a", "text": "SELECT * FROM Customers WHERE email IS NULL", "correct": True},
            {"id": "b", "text": "SELECT * FROM Customers WHERE email = NULL", "correct": False, "maps_to": "D08", "misconception": "Uses = NULL which evaluates to UNKNOWN and returns no rows"},
            {"id": "c", "text": "SELECT * FROM Customers WHERE email == ''", "correct": False, "maps_to": "D08", "misconception": "Uses double equals and confuses empty string with NULL"},
            {"id": "d", "text": "SELECT * FROM Customers WHERE email.isNull()", "correct": False, "maps_to": "D08", "misconception": "Uses object-oriented syntax not valid in standard SQL"}
        ],
        "explanation": "The IS NULL predicate is the only standard SQL syntax for testing whether an attribute value is NULL.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_B_02",
        "concept": "D08",
        "family": "B",
        "difficulty": 2,
        "prompt": "Which pattern finds all names starting with 'A' and having at least 3 characters in length?",
        "options": [
            {"id": "a", "text": "WHERE name LIKE 'A__%'", "correct": True},
            {"id": "b", "text": "WHERE name LIKE 'A%'", "correct": False, "maps_to": "D08", "misconception": "Matches any name starting with A, including names with only 1 or 2 characters"},
            {"id": "c", "text": "WHERE name LIKE 'A___'", "correct": False, "maps_to": "D08", "misconception": "Matches names of exactly 4 characters only"},
            {"id": "d", "text": "WHERE name LIKE 'A*'", "correct": False, "maps_to": "D08", "misconception": "Asterisk is regex/glob syntax, not standard SQL LIKE syntax"}
        ],
        "explanation": "'A__%' requires 'A' followed by at least two characters ('__'), followed by zero or more characters ('%'), ensuring minimum length 3.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_B_03",
        "concept": "D08",
        "family": "B",
        "difficulty": 2,
        "prompt": "What is the difference between TRUNCATE TABLE and DELETE FROM table without a WHERE clause?",
        "options": [
            {"id": "a", "text": "TRUNCATE is a DDL operation that deallocates data pages quickly with minimal logging, while DELETE is DML that logs individual row removals", "correct": True},
            {"id": "b", "text": "TRUNCATE only deletes the first 10 rows", "correct": False, "maps_to": "D08", "misconception": "Misinterprets TRUNCATE as a partial delete limit"},
            {"id": "c", "text": "DELETE drops the table structure from the catalog while TRUNCATE preserves it", "correct": False, "maps_to": "D08", "misconception": "DROP TABLE removes structure; both DELETE and TRUNCATE keep the table structure"},
            {"id": "d", "text": "There is no difference; they are exact synonyms", "correct": False, "maps_to": "D08", "misconception": "TRUNCATE has vastly different transaction log and performance characteristics"}
        ],
        "explanation": "TRUNCATE deallocates pages and cannot trigger ON DELETE triggers; DELETE removes rows individually through transactional DML logging.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_B_04",
        "concept": "D08",
        "family": "B",
        "difficulty": 3,
        "prompt": "When sorting a table using: SELECT name, score FROM Results ORDER BY score DESC, where do rows with NULL scores appear in standard SQL?",
        "options": [
            {"id": "a", "text": "At the very top (first), unless overridden by NULLS LAST", "correct": True},
            {"id": "b", "text": "Always at the bottom regardless of ASC or DESC", "correct": False, "maps_to": "D08", "misconception": "Under standard SQL DESC order, NULLs are treated as larger than all known values and appear first"},
            {"id": "c", "text": "Rows with NULL are omitted completely from the output", "correct": False, "maps_to": "D08", "misconception": "ORDER BY sorts all rows; it does not filter rows like WHERE"},
            {"id": "d", "text": "In the middle of the result set", "correct": False, "maps_to": "D08", "misconception": "NULLs are never sorted into the middle of numbers"}
        ],
        "explanation": "Under standard SQL, NULLs are treated as higher than all values. In DESC order, NULLs appear first (unless NULLS LAST is specified).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D08_B_05",
        "concept": "D08",
        "family": "B",
        "difficulty": 1,
        "prompt": "What SQL statement is used to modify existing row values in a database table?",
        "options": [
            {"id": "a", "text": "UPDATE", "correct": True},
            {"id": "b", "text": "ALTER", "correct": False, "maps_to": "D01", "misconception": "ALTER modifies table structure (DDL), UPDATE modifies table data rows (DML)"},
            {"id": "c", "text": "MODIFY", "correct": False, "maps_to": "D08", "misconception": "MODIFY is a sub-clause in ALTER TABLE in some dialects, not the row update statement"},
            {"id": "d", "text": "SET", "correct": False, "maps_to": "D08", "misconception": "SET is a clause within UPDATE, not the top-level command"}
        ],
        "explanation": "UPDATE table_name SET col = val WHERE condition is the standard statement to modify existing table rows.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D09: SQL Joins (11 questions)
    # ==========================================
    {
        "id": "Q_D09_A_01",
        "concept": "D09",
        "family": "A",
        "difficulty": 1,
        "prompt": "What type of join returns only rows where there is a match in both joined tables?",
        "options": [
            {"id": "a", "text": "INNER JOIN", "correct": True},
            {"id": "b", "text": "LEFT OUTER JOIN", "correct": False, "maps_to": "D09", "misconception": "LEFT JOIN also returns unmatched rows from the left table"},
            {"id": "c", "text": "FULL OUTER JOIN", "correct": False, "maps_to": "D09", "misconception": "FULL JOIN returns unmatched rows from both tables"},
            {"id": "d", "text": "CROSS JOIN", "correct": False, "maps_to": "D09", "misconception": "CROSS JOIN returns Cartesian product regardless of matches"}
        ],
        "explanation": "INNER JOIN evaluates the join condition and keeps only rows where the predicate is true in both tables.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_A_02",
        "concept": "D09",
        "family": "A",
        "difficulty": 2,
        "prompt": "In a query: Customers c LEFT JOIN Orders o ON c.id = o.customer_id, what appears in the orders columns for customers who have never placed an order?",
        "options": [
            {"id": "a", "text": "NULL values across all columns of Orders", "correct": True},
            {"id": "b", "text": "Zero (0) across all columns", "correct": False, "maps_to": "D09", "misconception": "Assumes database substitutes zeros for missing joined records"},
            {"id": "c", "text": "Those customers are excluded from the result", "correct": False, "maps_to": "D09", "misconception": "Describes INNER JOIN behavior; LEFT JOIN preserves all left table rows"},
            {"id": "d", "text": "The string 'N/A' in all columns", "correct": False, "maps_to": "D09", "misconception": "DBMS does not insert string literals for missing join attributes"}
        ],
        "explanation": "LEFT OUTER JOIN preserves all rows from the left table, padding missing right-table columns with NULLs.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_A_03",
        "concept": "D09",
        "family": "A",
        "difficulty": 2,
        "prompt": "What occurs when performing a CROSS JOIN between table A (5 rows) and table B (10 rows)?",
        "options": [
            {"id": "a", "text": "A Cartesian product containing 50 rows", "correct": True},
            {"id": "b", "text": "15 rows formed by unioning both tables", "correct": False, "maps_to": "D07", "misconception": "Adds row counts instead of computing Cartesian product"},
            {"id": "c", "text": "5 rows matching on common keys", "correct": False, "maps_to": "D09", "misconception": "CROSS JOIN does not use a key match predicate"},
            {"id": "d", "text": "A runtime error unless an ON clause is specified", "correct": False, "maps_to": "D09", "misconception": "CROSS JOIN does not take an ON clause"}
        ],
        "explanation": "CROSS JOIN produces the Cartesian product of the two tables (5 × 10 = 50 rows).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_A_04",
        "concept": "D09",
        "family": "A",
        "difficulty": 3,
        "prompt": "Consider the query: SELECT * FROM Employees e LEFT JOIN Departments d ON e.dept_id = d.id WHERE d.name = 'Finance'. What is the practical effect of this WHERE clause?",
        "options": [
            {"id": "a", "text": "It converts the LEFT JOIN into an INNER JOIN because employees without a department have NULL d.name, which fails the WHERE filter", "correct": True},
            {"id": "b", "text": "It includes all employees, displaying 'Finance' for everyone", "correct": False, "maps_to": "D09", "misconception": "WHERE filters the output rows after the join"},
            {"id": "c", "text": "It raises a syntax error", "correct": False, "maps_to": "D09", "misconception": "This is completely valid SQL syntax with unexpected logical consequences"},
            {"id": "d", "text": "It returns only employees without a department", "correct": False, "maps_to": "D09", "misconception": "Employees without departments have NULL d.name, filtered out by WHERE"}
        ],
        "explanation": "Filtering the right table's columns in the WHERE clause removes rows where the right side was NULL, unintentionally converting the LEFT JOIN into an INNER JOIN.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_A_05",
        "concept": "D09",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is a self-join in SQL?",
        "options": [
            {"id": "a", "text": "A join in which a table is joined with itself, using table aliases to distinguish the two instances", "correct": True},
            {"id": "b", "text": "A join that runs automatically without an ON clause", "correct": False, "maps_to": "D09", "misconception": "Confuses self-join with natural join or cross join"},
            {"id": "c", "text": "A join connecting two identical tables in different databases", "correct": False, "maps_to": "D09", "misconception": "Self-join involves a single table joined to itself"},
            {"id": "d", "text": "A join that automatically locks rows during write transactions", "correct": False, "maps_to": "D16", "misconception": "Confuses table self-referencing with concurrency locking"}
        ],
        "explanation": "A self-join joins a table to itself (commonly used for hierarchical structures like Employees and Managers), requiring table aliases.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_A_06",
        "concept": "D09",
        "family": "A",
        "difficulty": 1,
        "prompt": "Which join type returns all rows from both tables, filling with NULLs on either side when no match exists?",
        "options": [
            {"id": "a", "text": "FULL OUTER JOIN", "correct": True},
            {"id": "b", "text": "INNER JOIN", "correct": False, "maps_to": "D09", "misconception": "INNER JOIN discards unmatched rows from both tables"},
            {"id": "c", "text": "LEFT JOIN", "correct": False, "maps_to": "D09", "misconception": "LEFT JOIN only preserves unmatched rows from the left table"},
            {"id": "d", "text": "SEMI JOIN", "correct": False, "maps_to": "D09", "misconception": "SEMI JOIN tests existence without returning combined rows"}
        ],
        "explanation": "FULL OUTER JOIN combines the results of both LEFT and RIGHT outer joins, returning all rows and padding non-matches with NULLs.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_B_01",
        "concept": "D09",
        "family": "B",
        "difficulty": 1,
        "prompt": "Which query correctly finds all Customers who have NEVER placed any order?",
        "options": [
            {"id": "a", "text": "SELECT c.id FROM Customers c LEFT JOIN Orders o ON c.id = o.customer_id WHERE o.id IS NULL", "correct": True},
            {"id": "b", "text": "SELECT c.id FROM Customers c INNER JOIN Orders o ON c.id = o.customer_id WHERE o.id IS NULL", "correct": False, "maps_to": "D09", "misconception": "INNER JOIN discards unmatched customers before WHERE is evaluated"},
            {"id": "c", "text": "SELECT c.id FROM Customers c RIGHT JOIN Orders o ON c.id = o.customer_id WHERE c.id IS NULL", "correct": False, "maps_to": "D09", "misconception": "Finds orphan orders without customers, not customers without orders"},
            {"id": "d", "text": "SELECT c.id FROM Customers c CROSS JOIN Orders o WHERE o.id = 0", "correct": False, "maps_to": "D09", "misconception": "Cross join with arbitrary filter fails to detect absence of orders"}
        ],
        "explanation": "The 'anti-join' pattern uses a LEFT JOIN and filters for rows where the right table's primary key IS NULL.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_B_02",
        "concept": "D09",
        "family": "B",
        "difficulty": 2,
        "prompt": "What is the key difference between placing a filter predicate in the ON clause versus the WHERE clause of a LEFT JOIN?",
        "options": [
            {"id": "a", "text": "The ON clause condition determines which right-table rows qualify for matching (unmatched left rows still appear), whereas the WHERE clause filters the entire resulting row after the join", "correct": True},
            {"id": "b", "text": "There is no difference; modern query optimizers treat them identically", "correct": False, "maps_to": "D09", "misconception": "In outer joins, ON vs WHERE produces completely different results"},
            {"id": "c", "text": "The ON clause cannot use comparison operators like '>'", "correct": False, "maps_to": "D09", "misconception": "ON clauses can contain any boolean predicate"},
            {"id": "d", "text": "The WHERE clause runs before the tables are joined", "correct": False, "maps_to": "D18", "misconception": "WHERE filters the combined rows produced by the FROM/JOIN clause"}
        ],
        "explanation": "In outer joins, filtering the right table in ON preserves left table rows with NULL padding; filtering in WHERE removes the entire row.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_B_03",
        "concept": "D09",
        "family": "B",
        "difficulty": 2,
        "prompt": "An employee table has columns (EmpID, Name, ManagerID). Which query lists every employee along with their manager's name?",
        "options": [
            {"id": "a", "text": "SELECT e.Name, m.Name AS ManagerName FROM Employees e LEFT JOIN Employees m ON e.ManagerID = m.EmpID", "correct": True},
            {"id": "b", "text": "SELECT e.Name, m.Name FROM Employees e, Employees m WHERE e.EmpID = m.EmpID", "correct": False, "maps_to": "D09", "misconception": "Joins each employee with themselves instead of their manager"},
            {"id": "c", "text": "SELECT Name FROM Employees WHERE ManagerID IS NULL", "correct": False, "maps_to": "D08", "misconception": "Only returns employees without a manager (e.g. CEO)"},
            {"id": "d", "text": "SELECT e.Name, m.Name FROM Employees e FULL JOIN Departments m ON e.ManagerID = m.DeptID", "correct": False, "maps_to": "D09", "misconception": "Joins to wrong table (Departments instead of Employees)"}
        ],
        "explanation": "A self-join with aliases 'e' (employee) and 'm' (manager) linked by e.ManagerID = m.EmpID correctly pairs employees with managers.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_B_04",
        "concept": "D09",
        "family": "B",
        "difficulty": 3,
        "prompt": "If table A has 3 rows all containing value 1 in column x, and table B has 4 rows all containing value 1 in column x, how many rows are returned by: SELECT * FROM A JOIN B ON A.x = B.x?",
        "options": [
            {"id": "a", "text": "12 rows", "correct": True},
            {"id": "b", "text": "3 rows", "correct": False, "maps_to": "D09", "misconception": "Assumes join stops after matching each left row once"},
            {"id": "c", "text": "4 rows", "correct": False, "maps_to": "D09", "misconception": "Assumes join produces only right row count"},
            {"id": "d", "text": "1 row", "correct": False, "maps_to": "D09", "misconception": "Assumes distinct values are joined rather than individual multiset rows"}
        ],
        "explanation": "Since SQL joins work on multisets, every matching row in A pairs with every matching row in B: 3 × 4 = 12 rows.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D09_B_05",
        "concept": "D09",
        "family": "B",
        "difficulty": 1,
        "prompt": "What is a Non-Equi Join in SQL?",
        "options": [
            {"id": "a", "text": "A join condition that uses comparison operators other than '=' (e.g. '<', '>=', 'BETWEEN')", "correct": True},
            {"id": "b", "text": "A join between tables that have different numbers of columns", "correct": False, "maps_to": "D09", "misconception": "Non-equi refers to comparison operator, not table arity"},
            {"id": "c", "text": "A join that fails due to constraint errors", "correct": False, "maps_to": "D04", "misconception": "Non-equi is a valid join syntax, not an error state"},
            {"id": "d", "text": "A join that only returns rows where columns are unequal", "correct": False, "maps_to": "D09", "misconception": "Non-equi includes range operators (<, >, BETWEEN), not merely '!='"}
        ],
        "explanation": "An equi-join uses '=' in the join condition. Any join using other operators (<, <=, >, >=, BETWEEN) is a non-equi join.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D10: Aggregation & GROUP BY (11 questions)
    # ==========================================
    {
        "id": "Q_D10_A_01",
        "concept": "D10",
        "family": "A",
        "difficulty": 1,
        "prompt": "What is the difference between COUNT(*) and COUNT(column_name) in SQL?",
        "options": [
            {"id": "a", "text": "COUNT(*) counts all rows including those with NULLs, while COUNT(column_name) counts only non-null values in that column", "correct": True},
            {"id": "b", "text": "COUNT(*) counts only unique rows while COUNT(column_name) counts all duplicates", "correct": False, "maps_to": "D10", "misconception": "COUNT(DISTINCT col) counts unique rows, not COUNT(*)"},
            {"id": "c", "text": "COUNT(*) only works on tables with primary keys", "correct": False, "maps_to": "D03", "misconception": "COUNT(*) functions on any query result set"},
            {"id": "d", "text": "There is no difference; they always return identical numbers", "correct": False, "maps_to": "D10", "misconception": "Ignored the null-skipping behavior of column aggregations"}
        ],
        "explanation": "COUNT(*) counts total tuples. COUNT(column_name) ignores rows where that column is NULL.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_A_02",
        "concept": "D10",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is the key functional difference between the WHERE clause and the HAVING clause?",
        "options": [
            {"id": "a", "text": "WHERE filters individual rows before grouping; HAVING filters aggregated groups after GROUP BY", "correct": True},
            {"id": "b", "text": "HAVING runs before rows are read from disk; WHERE runs after", "correct": False, "maps_to": "D18", "misconception": "Inverts the logical processing phases of SQL"},
            {"id": "c", "text": "WHERE only works with numbers; HAVING only works with strings", "correct": False, "maps_to": "D10", "misconception": "Clauses are not restricted to specific data types"},
            {"id": "d", "text": "WHERE can use aggregate functions like SUM(x) > 100", "correct": False, "maps_to": "D10", "misconception": "Aggregate functions cannot appear in the WHERE clause"}
        ],
        "explanation": "WHERE filters base rows prior to aggregation. HAVING filters grouped rows using aggregate conditions (e.g. HAVING COUNT(*) > 5).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_A_03",
        "concept": "D10",
        "family": "A",
        "difficulty": 2,
        "prompt": "A table has a column 'score' with values [10, 20, NULL]. What does the query: SELECT AVG(score) FROM T return?",
        "options": [
            {"id": "a", "text": "15 (the sum 30 divided by 2 non-null rows)", "correct": True},
            {"id": "b", "text": "10 (the sum 30 divided by all 3 rows)", "correct": False, "maps_to": "D10", "misconception": "Assumes aggregate AVG treats NULL as 0 and divides by total rows"},
            {"id": "c", "text": "NULL", "correct": False, "maps_to": "D10", "misconception": "SQL aggregate functions ignore NULLs rather than evaluating to NULL"},
            {"id": "d", "text": "A runtime divide-by-zero error", "correct": False, "maps_to": "D10", "misconception": "Divide-by-zero only occurs when the non-null count is zero"}
        ],
        "explanation": "Standard SQL aggregate functions (SUM, AVG, MIN, MAX) ignore NULL values. AVG computes 30 / 2 = 15.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_A_04",
        "concept": "D10",
        "family": "A",
        "difficulty": 3,
        "prompt": "Why does the following query cause an error in standard SQL: SELECT department_id, employee_name, AVG(salary) FROM Employees GROUP BY department_id?",
        "options": [
            {"id": "a", "text": "employee_name is neither an aggregate function nor included in the GROUP BY clause", "correct": True},
            {"id": "b", "text": "AVG() cannot be calculated on salary columns", "correct": False, "maps_to": "D10", "misconception": "Salary is numeric and completely valid for AVG"},
            {"id": "c", "text": "GROUP BY cannot be used with department_id", "correct": False, "maps_to": "D10", "misconception": "department_id is a perfectly valid grouping attribute"},
            {"id": "d", "text": "The query lacks a HAVING clause", "correct": False, "maps_to": "D10", "misconception": "HAVING clauses are entirely optional"}
        ],
        "explanation": "In standard SQL, any non-aggregated column in the SELECT list must appear in the GROUP BY clause.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_A_05",
        "concept": "D10",
        "family": "A",
        "difficulty": 1,
        "prompt": "What does SUM(bonus) return when executed on a table where every row has bonus = NULL?",
        "options": [
            {"id": "a", "text": "NULL", "correct": True},
            {"id": "b", "text": "0", "correct": False, "maps_to": "D10", "misconception": "Assumes SUM defaults to zero when no non-null values exist"},
            {"id": "c", "text": "-1", "correct": False, "maps_to": "D10", "misconception": "SQL does not return sentinel error codes like -1"},
            {"id": "d", "text": "Syntax Error", "correct": False, "maps_to": "D10", "misconception": "The query is valid; it evaluates to NULL"}
        ],
        "explanation": "When an aggregate like SUM, AVG, MIN, or MAX is evaluated over an empty set or a set of only NULLs, it returns NULL (only COUNT returns 0).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_A_06",
        "concept": "D10",
        "family": "A",
        "difficulty": 2,
        "prompt": "How does GROUP BY treat rows where the grouping column is NULL?",
        "options": [
            {"id": "a", "text": "All rows with NULL in the grouping column are gathered together into a single group", "correct": True},
            {"id": "b", "text": "Rows with NULL are silently discarded before grouping", "correct": False, "maps_to": "D10", "misconception": "GROUP BY does not drop NULLs; they form their own group"},
            {"id": "c", "text": "Each row with NULL creates its own separate individual group", "correct": False, "maps_to": "D10", "misconception": "In GROUP BY, NULLs are treated as equivalent for grouping"},
            {"id": "d", "text": "An error is thrown because NULLs cannot be grouped", "correct": False, "maps_to": "D10", "misconception": "GROUP BY handles NULLs cleanly in standard SQL"}
        ],
        "explanation": "In SQL GROUP BY, all NULL values in the grouping column are clustered into a single collective group.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_B_01",
        "concept": "D10",
        "family": "B",
        "difficulty": 1,
        "prompt": "Which query correctly finds all departments that employ more than 10 employees?",
        "options": [
            {"id": "a", "text": "SELECT dept_id, COUNT(*) FROM Employees GROUP BY dept_id HAVING COUNT(*) > 10", "correct": True},
            {"id": "b", "text": "SELECT dept_id, COUNT(*) FROM Employees WHERE COUNT(*) > 10 GROUP BY dept_id", "correct": False, "maps_to": "D10", "misconception": "Aggregate functions are illegal in the WHERE clause"},
            {"id": "c", "text": "SELECT dept_id FROM Employees GROUP BY dept_id WHERE dept_id > 10", "correct": False, "maps_to": "D10", "misconception": "Filters department ID numbers instead of employee counts"},
            {"id": "d", "text": "SELECT dept_id FROM Employees HAVING COUNT(*) > 10", "correct": False, "maps_to": "D10", "misconception": "Lacks GROUP BY dept_id, aggregating the entire table into one row"}
        ],
        "explanation": "HAVING COUNT(*) > 10 filters the groups created by GROUP BY dept_id based on aggregate counts.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_B_02",
        "concept": "D10",
        "family": "B",
        "difficulty": 2,
        "prompt": "What does the expression COUNT(DISTINCT country) calculate?",
        "options": [
            {"id": "a", "text": "The count of unique, non-null country names present in the table", "correct": True},
            {"id": "b", "text": "The count of all countries including duplicates and NULLs", "correct": False, "maps_to": "D10", "misconception": "Ignored DISTINCT and column non-null rules"},
            {"id": "c", "text": "The count of distinct countries, counting NULL as one country", "correct": False, "maps_to": "D10", "misconception": "COUNT(column) always skips NULL values"},
            {"id": "d", "text": "The total number of tables in the database", "correct": False, "maps_to": "D01", "misconception": "Confuses column aggregation with metadata catalog counts"}
        ],
        "explanation": "COUNT(DISTINCT col) eliminates duplicate values and ignores NULLs, counting only unique non-null values.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_B_03",
        "concept": "D10",
        "family": "B",
        "difficulty": 2,
        "prompt": "If a query groups by two attributes: GROUP BY Department, JobRole, how are groups formed?",
        "options": [
            {"id": "a", "text": "Each unique combination of Department and JobRole forms an individual group", "correct": True},
            {"id": "b", "text": "Two independent result sets are generated and concatenated", "correct": False, "maps_to": "D10", "misconception": "GROUP BY does not create separate result sets"},
            {"id": "c", "text": "Rows are grouped solely by Department; JobRole is ignored", "correct": False, "maps_to": "D10", "misconception": "All specified grouping columns contribute to group identity"},
            {"id": "d", "text": "An error is thrown because only one column is permitted in GROUP BY", "correct": False, "maps_to": "D10", "misconception": "Multiple columns are completely supported in GROUP BY"}
        ],
        "explanation": "Grouping by multiple attributes creates a group for each unique tuple combination of those attributes.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_B_04",
        "concept": "D10",
        "family": "B",
        "difficulty": 3,
        "prompt": "In what order are the logical processing phases of a SQL query evaluated?",
        "options": [
            {"id": "a", "text": "FROM/JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY", "correct": True},
            {"id": "b", "text": "SELECT -> FROM -> WHERE -> GROUP BY -> HAVING -> ORDER BY", "correct": False, "maps_to": "D18", "misconception": "Confuses written query syntax order with logical evaluation order"},
            {"id": "c", "text": "WHERE -> FROM -> SELECT -> GROUP BY -> ORDER BY", "correct": False, "maps_to": "D18", "misconception": "FROM/JOIN must be evaluated before WHERE filters rows"},
            {"id": "d", "text": "ORDER BY -> GROUP BY -> HAVING -> SELECT -> FROM", "correct": False, "maps_to": "D18", "misconception": "ORDER BY is the final presentation sorting step"}
        ],
        "explanation": "Logically, SQL evaluates tables (FROM/JOIN), filters rows (WHERE), groups them (GROUP BY), filters groups (HAVING), projects columns (SELECT), and sorts (ORDER BY).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D10_B_05",
        "concept": "D10",
        "family": "B",
        "difficulty": 1,
        "prompt": "What does COUNT(*) return when executed against a table that contains zero rows?",
        "options": [
            {"id": "a", "text": "0", "correct": True},
            {"id": "b", "text": "NULL", "correct": False, "maps_to": "D10", "misconception": "COUNT is the only aggregate function that returns 0 instead of NULL on empty sets"},
            {"id": "c", "text": "An empty result set", "correct": False, "maps_to": "D10", "misconception": "Aggregate without GROUP BY always returns exactly one row"},
            {"id": "d", "text": "A division by zero exception", "correct": False, "maps_to": "D10", "misconception": "COUNT(*) performs counting, not division"}
        ],
        "explanation": "COUNT(*) on an empty table returns 0. (Unlike SUM or AVG, which return NULL).",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D11: Subqueries and Views (11 questions)
    # ==========================================
    {
        "id": "Q_D11_A_01",
        "concept": "D11",
        "family": "A",
        "difficulty": 1,
        "prompt": "What defines a correlated subquery in SQL?",
        "options": [
            {"id": "a", "text": "A subquery that references one or more columns from the outer query, evaluating once for each outer row", "correct": True},
            {"id": "b", "text": "A subquery that executes only once independently before the outer query runs", "correct": False, "maps_to": "D11", "misconception": "Describes an uncorrelated (independent) subquery"},
            {"id": "c", "text": "A subquery that returns exactly two columns", "correct": False, "maps_to": "D11", "misconception": "Subquery shape does not define correlation"},
            {"id": "d", "text": "A subquery that creates a temporary table in the file system", "correct": False, "maps_to": "D01", "misconception": "Confuses query evaluation with physical temp storage"}
        ],
        "explanation": "A correlated subquery references values from the outer query and must logically be re-evaluated for each candidate row in the outer query.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_A_02",
        "concept": "D11",
        "family": "A",
        "difficulty": 2,
        "prompt": "What does the SQL predicate EXISTS (subquery) return?",
        "options": [
            {"id": "a", "text": "TRUE if the subquery returns at least one row, and FALSE otherwise", "correct": True},
            {"id": "b", "text": "The numeric count of rows returned by the subquery", "correct": False, "maps_to": "D11", "misconception": "EXISTS returns a boolean, not an integer count"},
            {"id": "c", "text": "NULL if any row in the subquery contains a NULL value", "correct": False, "maps_to": "D11", "misconception": "EXISTS checks for row existence; internal NULL attribute values do not affect it"},
            {"id": "d", "text": "TRUE only if all rows in the subquery match the outer row", "correct": False, "maps_to": "D11", "misconception": "Confuses EXISTS with universal comparison operators like ALL"}
        ],
        "explanation": "EXISTS evaluates to TRUE as soon as the subquery produces at least one tuple, regardless of column values.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_A_03",
        "concept": "D11",
        "family": "A",
        "difficulty": 2,
        "prompt": "Why can the query: WHERE x NOT IN (SELECT y FROM T) return zero rows unexpectedly if table T contains even a single NULL value in column y?",
        "options": [
            {"id": "a", "text": "Because 'x NOT IN (..., NULL)' expands to 'x != val AND x != NULL', and since 'x != NULL' is UNKNOWN, the entire condition evaluates to UNKNOWN", "correct": True},
            {"id": "b", "text": "Because NOT IN automatically deletes all rows from table T", "correct": False, "maps_to": "D08", "misconception": "A query predicate does not execute deletion DML"},
            {"id": "c", "text": "Because SQL engines crash when reading NULL values inside subqueries", "correct": False, "maps_to": "D11", "misconception": "Engine handles 3VL cleanly; the boolean logic simply yields UNKNOWN"},
            {"id": "d", "text": "Because NOT IN requires an index to be present", "correct": False, "maps_to": "D17", "misconception": "Index presence affects performance, not boolean 3VL semantics"}
        ],
        "explanation": "Under 3VL, x != NULL evaluates to UNKNOWN. In NOT IN, conditions are ANDed together; any UNKNOWN prevents the expression from ever evaluating to TRUE.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_A_04",
        "concept": "D11",
        "family": "A",
        "difficulty": 1,
        "prompt": "What is a database View?",
        "options": [
            {"id": "a", "text": "A virtual table defined by a stored SQL query whose contents are dynamically computed when referenced", "correct": True},
            {"id": "b", "text": "A permanent physical duplicate copy of base tables stored on disk", "correct": False, "maps_to": "D01", "misconception": "Standard views do not duplicate data physically on disk (materialized views do)"},
            {"id": "c", "text": "A GUI interface window in database administration tools", "correct": False, "maps_to": "D01", "misconception": "Confuses client GUI window with relational database view objects"},
            {"id": "d", "text": "A table that cannot be queried with SELECT statements", "correct": False, "maps_to": "D08", "misconception": "Views can be queried exactly like base tables"}
        ],
        "explanation": "A view is a stored query definition presenting a virtual table derived from underlying base relations.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_A_05",
        "concept": "D11",
        "family": "A",
        "difficulty": 3,
        "prompt": "What condition generally prevents a database View from being directly updatable via INSERT or UPDATE statements?",
        "options": [
            {"id": "a", "text": "The view definition includes GROUP BY, DISTINCT, aggregate functions, or set operations", "correct": True},
            {"id": "b", "text": "The view references more than three columns", "correct": False, "maps_to": "D11", "misconception": "Column count has no restriction on view updatability"},
            {"id": "c", "text": "The underlying table has a primary key defined", "correct": False, "maps_to": "D03", "misconception": "Underlying primary keys make view updates easier, not prohibited"},
            {"id": "d", "text": "The view was created by a database administrator", "correct": False, "maps_to": "D01", "misconception": "User ownership does not dictate SQL view updatability"}
        ],
        "explanation": "A view cannot be updated directly if it involves aggregation, GROUP BY, DISTINCT, or UNION, because row updates cannot map unambiguously to base table tuples.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_A_06",
        "concept": "D11",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is a Common Table Expression (CTE) defined using the WITH clause in SQL?",
        "options": [
            {"id": "a", "text": "A named temporary result set that exists solely within the execution scope of a single SQL statement", "correct": True},
            {"id": "b", "text": "A permanent table stored permanently in the system catalog", "correct": False, "maps_to": "D01", "misconception": "CTEs are transient query-scoped expressions, not persistent catalog tables"},
            {"id": "c", "text": "A database constraint that checks for common table errors", "correct": False, "maps_to": "D04", "misconception": "Confuses query refactoring syntax with integrity constraints"},
            {"id": "d", "text": "A stored procedure compiled into machine code", "correct": False, "maps_to": "D08", "misconception": "Confuses CTEs with compiled procedures"}
        ],
        "explanation": "A CTE provides a readable, modular way to define a temporary named result set for use within a single SELECT, INSERT, UPDATE, or DELETE query.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_B_01",
        "concept": "D11",
        "family": "B",
        "difficulty": 1,
        "prompt": "What type of subquery returns exactly one single value (one row and one column)?",
        "options": [
            {"id": "a", "text": "Scalar subquery", "correct": True},
            {"id": "b", "text": "Table subquery", "correct": False, "maps_to": "D11", "misconception": "Table subqueries return multiple rows and columns"},
            {"id": "c", "text": "Correlated vector subquery", "correct": False, "maps_to": "D11", "misconception": "Invented terminology"},
            {"id": "d", "text": "Partition subquery", "correct": False, "maps_to": "D11", "misconception": "Confuses window partitioning with scalar subqueries"}
        ],
        "explanation": "A scalar subquery returns exactly one value (1 row, 1 column) and can be used in expressions where a single value is expected.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_B_02",
        "concept": "D11",
        "family": "B",
        "difficulty": 2,
        "prompt": "How does the comparison operator '> ALL (subquery)' behave?",
        "options": [
            {"id": "a", "text": "It evaluates to TRUE only if the outer value is strictly greater than every value returned by the subquery", "correct": True},
            {"id": "b", "text": "It evaluates to TRUE if the outer value is greater than at least one value in the subquery", "correct": False, "maps_to": "D11", "misconception": "Describes '> ANY' instead of '> ALL'"},
            {"id": "c", "text": "It returns the average of all subquery rows", "correct": False, "maps_to": "D10", "misconception": "ALL is a comparison quantifier, not an aggregate function"},
            {"id": "d", "text": "It raises a syntax error if the subquery returns more than 1 row", "correct": False, "maps_to": "D11", "misconception": "ALL is specifically designed to handle multi-row subqueries"}
        ],
        "explanation": "val > ALL (subquery) requires val to be greater than the maximum value produced by the subquery.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_B_03",
        "concept": "D11",
        "family": "B",
        "difficulty": 2,
        "prompt": "Which query correctly finds all employees whose salary exceeds the average salary of their own department?",
        "options": [
            {"id": "a", "text": "SELECT * FROM Employees e WHERE salary > (SELECT AVG(salary) FROM Employees WHERE dept_id = e.dept_id)", "correct": True},
            {"id": "b", "text": "SELECT * FROM Employees WHERE salary > AVG(salary)", "correct": False, "maps_to": "D10", "misconception": "Aggregate functions cannot appear in the WHERE clause without a subquery"},
            {"id": "c", "text": "SELECT * FROM Employees WHERE salary > (SELECT AVG(salary) FROM Employees)", "correct": False, "maps_to": "D11", "misconception": "Compares against company-wide average instead of department average"},
            {"id": "d", "text": "SELECT * FROM Employees GROUP BY dept_id HAVING salary > AVG(salary)", "correct": False, "maps_to": "D10", "misconception": "Cannot filter individual employee salaries in HAVING"}
        ],
        "explanation": "This requires a correlated subquery where the inner query filters by the outer employee's department ID (dept_id = e.dept_id).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_B_04",
        "concept": "D11",
        "family": "B",
        "difficulty": 3,
        "prompt": "What is the difference between a standard View and a Materialized View?",
        "options": [
            {"id": "a", "text": "A standard view executes its query on-demand at runtime, while a materialized view stores query results physically on disk and requires refreshing", "correct": True},
            {"id": "b", "text": "Standard views can only contain numeric data, while materialized views store strings", "correct": False, "maps_to": "D11", "misconception": "Materialization has nothing to do with data types"},
            {"id": "c", "text": "Materialized views can never be indexed", "correct": False, "maps_to": "D17", "misconception": "Materialized views can have indexes created on them to boost queries"},
            {"id": "d", "text": "There is no difference; they are interchangeable keywords", "correct": False, "maps_to": "D11", "misconception": "Materialized views physically persist table data while standard views do not"}
        ],
        "explanation": "Materialized views persist physical pre-computed result sets on disk, improving read performance at the expense of storage and refresh overhead.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D11_B_05",
        "concept": "D11",
        "family": "B",
        "difficulty": 1,
        "prompt": "Can a subquery appear in the FROM clause of an outer SQL query?",
        "options": [
            {"id": "a", "text": "Yes, it is known as a derived table (or inline view) and must typically be given a table alias", "correct": True},
            {"id": "b", "text": "No, subqueries can only appear in the WHERE clause", "correct": False, "maps_to": "D11", "misconception": "Subqueries can appear in SELECT, FROM, WHERE, and HAVING clauses"},
            {"id": "c", "text": "Only if the subquery contains no JOIN operations", "correct": False, "maps_to": "D11", "misconception": "Derived tables can include any valid SQL query including joins"},
            {"id": "d", "text": "Only if the subquery returns exactly one row", "correct": False, "maps_to": "D11", "misconception": "FROM clause subqueries commonly return multiple rows"}
        ],
        "explanation": "A subquery in the FROM clause acts as a derived table and can be queried and joined like any base table.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D12: Functional Dependencies (11 questions)
    # ==========================================
    {
        "id": "Q_D12_A_01",
        "concept": "D12",
        "family": "A",
        "difficulty": 1,
        "prompt": "What does the functional dependency X -> Y formally state in relation schema R?",
        "options": [
            {"id": "a", "text": "For any two tuples t1 and t2 in R, if t1[X] = t2[X], then t1[Y] must equal t2[Y]", "correct": True},
            {"id": "b", "text": "Attribute X and attribute Y must have the exact same data type", "correct": False, "maps_to": "D12", "misconception": "Functional dependencies define value mappings, not data type equality"},
            {"id": "c", "text": "Y is a foreign key pointing to X", "correct": False, "maps_to": "D04", "misconception": "Confuses functional dependency with referential integrity"},
            {"id": "d", "text": "X and Y are always candidate keys of R", "correct": False, "maps_to": "D03", "misconception": "Functional dependencies can hold between arbitrary attribute sets"}
        ],
        "explanation": "X -> Y means that whenever two tuples agree on attributes X, they must also agree on attributes Y.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_A_02",
        "concept": "D12",
        "family": "A",
        "difficulty": 2,
        "prompt": "According to Armstrong's Axioms, what is the Transitivity rule?",
        "options": [
            {"id": "a", "text": "If X -> Y and Y -> Z hold, then X -> Z holds", "correct": True},
            {"id": "b", "text": "If Y ⊆ X, then X -> Y holds", "correct": False, "maps_to": "D12", "misconception": "Describes the Reflexivity rule"},
            {"id": "c", "text": "If X -> Y holds, then XZ -> YZ holds", "correct": False, "maps_to": "D12", "misconception": "Describes the Augmentation rule"},
            {"id": "d", "text": "If X -> Y and X -> Z hold, then X -> YZ holds", "correct": False, "maps_to": "D12", "misconception": "Describes the Union (Additivity) rule"}
        ],
        "explanation": "Transitivity states that if X determines Y and Y determines Z, then X determines Z.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_A_03",
        "concept": "D12",
        "family": "A",
        "difficulty": 2,
        "prompt": "Given relation R(A, B, C, D) with FDs: {A -> B, B -> C, C -> D}. What is the attribute closure {A}+?",
        "options": [
            {"id": "a", "text": "{A, B, C, D}", "correct": True},
            {"id": "b", "text": "{A, B}", "correct": False, "maps_to": "D12", "misconception": "Fails to apply transitive dependencies B -> C and C -> D"},
            {"id": "c", "text": "{A, D}", "correct": False, "maps_to": "D12", "misconception": "Omits intermediate dependent attributes B and C"},
            {"id": "d", "text": "{B, C, D}", "correct": False, "maps_to": "D12", "misconception": "Closure of A must always include A itself (reflexivity)"}
        ],
        "explanation": "Starting with {A}: A -> B adds B; B -> C adds C; C -> D adds D. Hence {A}+ = {A, B, C, D}.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_A_04",
        "concept": "D12",
        "family": "A",
        "difficulty": 1,
        "prompt": "What is a trivial functional dependency?",
        "options": [
            {"id": "a", "text": "A dependency X -> Y where Y is a subset of X (Y ⊆ X)", "correct": True},
            {"id": "b", "text": "A dependency that holds only when the table has zero rows", "correct": False, "maps_to": "D12", "misconception": "Trivial dependencies hold for all relations and all instances universally"},
            {"id": "c", "text": "A dependency between two primary key columns", "correct": False, "maps_to": "D03", "misconception": "Triviality is defined by subset inclusion, not primary key status"},
            {"id": "d", "text": "A dependency where X and Y share zero common attributes", "correct": False, "maps_to": "D12", "misconception": "Describes a completely non-trivial dependency (X ∩ Y = ∅)"}
        ],
        "explanation": "A dependency X -> Y is trivial if Y is a subset of X (e.g. {A, B} -> A).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_A_05",
        "concept": "D12",
        "family": "A",
        "difficulty": 3,
        "prompt": "Given relation R(A, B, C) with FD set F = {A -> B, B -> C, C -> A}. How many candidate keys does relation R have?",
        "options": [
            {"id": "a", "text": "3 candidate keys: {A}, {B}, and {C}", "correct": True},
            {"id": "b", "text": "1 candidate key: {A}", "correct": False, "maps_to": "D12", "misconception": "Overlooks that B+ and C+ also determine all attributes due to circular FDs"},
            {"id": "c", "text": "0 candidate keys", "correct": False, "maps_to": "D03", "misconception": "Every finite relation schema has at least one candidate key"},
            {"id": "d", "text": "None, {A, B, C} composite is the only key", "correct": False, "maps_to": "D03", "misconception": "Composite {A, B, C} is not minimal since each single attribute is sufficient"}
        ],
        "explanation": "A+ = {A, B, C}, B+ = {A, B, C}, and C+ = {A, B, C}. Each is minimal and unique, giving 3 candidate keys.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_A_06",
        "concept": "D12",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is the Augmentation rule in Armstrong's Axioms?",
        "options": [
            {"id": "a", "text": "If X -> Y holds, then XZ -> YZ holds for any attribute set Z", "correct": True},
            {"id": "b", "text": "If X -> Y and Y -> Z hold, then X -> Z holds", "correct": False, "maps_to": "D12", "misconception": "Describes Transitivity"},
            {"id": "c", "text": "If Y ⊆ X, then X -> Y holds", "correct": False, "maps_to": "D12", "misconception": "Describes Reflexivity"},
            {"id": "d", "text": "If X -> YZ holds, then X -> Y holds", "correct": False, "maps_to": "D12", "misconception": "Describes Decomposition"}
        ],
        "explanation": "Augmentation states that adding attribute set Z to both sides of a valid FD X -> Y yields another valid FD XZ -> YZ.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_B_01",
        "concept": "D12",
        "family": "B",
        "difficulty": 1,
        "prompt": "If X is a candidate key for relation R(A, B, C, D), what must attribute closure X+ be equal to?",
        "options": [
            {"id": "a", "text": "All attributes of R: {A, B, C, D}", "correct": True},
            {"id": "b", "text": "Only attribute X itself", "correct": False, "maps_to": "D12", "misconception": "A key must uniquely determine all attributes in the relation"},
            {"id": "c", "text": "The empty set", "correct": False, "maps_to": "D12", "misconception": "Attribute closure of any attribute set X always includes X itself"},
            {"id": "d", "text": "Only prime attributes", "correct": False, "maps_to": "D03", "misconception": "A candidate key determines both prime and non-prime attributes"}
        ],
        "explanation": "By definition, a candidate key functionally determines all attributes in the relation, so X+ contains every attribute in R.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_B_02",
        "concept": "D12",
        "family": "B",
        "difficulty": 2,
        "prompt": "What defines a canonical cover (or minimal cover) Fc of a set of functional dependencies F?",
        "options": [
            {"id": "a", "text": "An equivalent set of FDs with singleton right-hand sides, no extraneous attributes, and no redundant dependencies", "correct": True},
            {"id": "b", "text": "A set of FDs containing all possible Armstrong inferences", "correct": False, "maps_to": "D12", "misconception": "Describes the full closure F+, which is maximal, not minimal"},
            {"id": "c", "text": "A set containing only trivial dependencies", "correct": False, "maps_to": "D12", "misconception": "Minimal cover eliminates trivial dependencies"},
            {"id": "d", "text": "A set of FDs with the maximum number of attributes on the left", "correct": False, "maps_to": "D12", "misconception": "Extraneous attributes are eliminated, not maximized"}
        ],
        "explanation": "A canonical cover is minimal: every right-hand side is a single attribute, no extraneous attributes exist on left or right, and no FD is redundant.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_B_03",
        "concept": "D12",
        "family": "B",
        "difficulty": 2,
        "prompt": "Given relation R(A, B, C, D) and FDs: {A -> B, C -> D}. What is the candidate key of R?",
        "options": [
            {"id": "a", "text": "{A, C}", "correct": True},
            {"id": "b", "text": "{A}", "correct": False, "maps_to": "D12", "misconception": "{A}+ = {A, B}, which does not determine C or D"},
            {"id": "c", "text": "{C}", "correct": False, "maps_to": "D12", "misconception": "{C}+ = {C, D}, which does not determine A or B"},
            {"id": "d", "text": "{B, D}", "correct": False, "maps_to": "D12", "misconception": "{B, D} are dependent attributes with no outgoing FDs"}
        ],
        "explanation": "Neither A nor C appears on the right side of any FD, so both must be in any key. {A, C}+ = {A, B, C, D}, making {A, C} the minimal candidate key.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_B_04",
        "concept": "D12",
        "family": "B",
        "difficulty": 3,
        "prompt": "In the dependency AB -> C, if A -> C already holds in F, what is attribute B termed?",
        "options": [
            {"id": "a", "text": "An extraneous attribute", "correct": True},
            {"id": "b", "text": "A primary key", "correct": False, "maps_to": "D03", "misconception": "Extraneous attribute status has no relation to primary keys"},
            {"id": "c", "text": "A surrogate attribute", "correct": False, "maps_to": "D03", "misconception": "Surrogate keys are artificial IDs, not redundant FD components"},
            {"id": "d", "text": "A prime key", "correct": False, "maps_to": "D03", "misconception": "Attribute B is redundant in this FD"}
        ],
        "explanation": "An attribute in a functional dependency is extraneous if it can be removed from the left or right side without changing the closure of the FD set.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D12_B_05",
        "concept": "D12",
        "family": "B",
        "difficulty": 1,
        "prompt": "Can a functional dependency be verified as true solely by examining a single instance (state) of a relation?",
        "options": [
            {"id": "a", "text": "No, an instance can only disprove an FD; confirming an FD requires semantic domain knowledge of the enterprise", "correct": True},
            {"id": "b", "text": "Yes, if all current rows satisfy the FD, it is guaranteed to hold forever", "correct": False, "maps_to": "D12", "misconception": "A temporary snapshot can satisfy an FD coincidentally without being an enterprise constraint"},
            {"id": "c", "text": "Only if the instance contains more than 1000 rows", "correct": False, "maps_to": "D12", "misconception": "FDs are schema-level assertions, not empirical row-count thresholds"},
            {"id": "d", "text": "Yes, because FDs are calculated automatically by the database compiler", "correct": False, "maps_to": "D01", "misconception": "Database designers specify FDs based on real-world business rules"}
        ],
        "explanation": "A relation instance can only show that an FD is violated. Proving an FD holds universally requires knowledge of the business semantics.",
        "validation_status": "reviewed"
    }
]
