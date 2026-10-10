"""
Part 3 of 200 Question Bank:
Concepts D13, D14, D15, D16 (11 each) + D17, D18 (12 each) = 68 questions total
"""

QUESTIONS_PART3 = [
    # ==========================================
    # D13: Normalization (1NF to 3NF) (11 questions)
    # ==========================================
    {
        "id": "Q_D13_A_01",
        "concept": "D13",
        "family": "A",
        "difficulty": 1,
        "prompt": "What core condition is required for a relation to be in First Normal Form (1NF)?",
        "options": [
            {"id": "a", "text": "All attribute values must be atomic, with no repeating groups or composite/multivalued columns", "correct": True},
            {"id": "b", "text": "Every non-prime attribute must be fully functionally dependent on every candidate key", "correct": False, "maps_to": "D13", "misconception": "Describes Second Normal Form (2NF)"},
            {"id": "c", "text": "No non-prime attribute can be transitively dependent on any candidate key", "correct": False, "maps_to": "D13", "misconception": "Describes Third Normal Form (3NF)"},
            {"id": "d", "text": "All functional dependencies must have superkeys on the left-hand side", "correct": False, "maps_to": "D14", "misconception": "Describes Boyce-Codd Normal Form (BCNF)"}
        ],
        "explanation": "1NF requires that each column contain only atomic (indivisible) scalar values and that there are no repeating groups.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_A_02",
        "concept": "D13",
        "family": "A",
        "difficulty": 2,
        "prompt": "What defines a partial dependency that violates Second Normal Form (2NF)?",
        "options": [
            {"id": "a", "text": "A non-prime attribute depends on a proper subset of a composite candidate key", "correct": True},
            {"id": "b", "text": "A non-prime attribute determines another non-prime attribute", "correct": False, "maps_to": "D13", "misconception": "Describes transitive dependency (which violates 3NF)"},
            {"id": "c", "text": "A candidate key contains more than two attributes", "correct": False, "maps_to": "D03", "misconception": "Composite keys with multiple attributes are entirely valid in 2NF"},
            {"id": "d", "text": "A relation contains foreign keys with NULL values", "correct": False, "maps_to": "D04", "misconception": "NULL foreign keys do not violate normal forms"}
        ],
        "explanation": "2NF requires 1NF and no partial dependencies: no non-prime attribute may depend on only a part of a composite candidate key.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_A_03",
        "concept": "D13",
        "family": "A",
        "difficulty": 2,
        "prompt": "In relation Orders(OrderID, CustomerID, CustomerCity), with candidate key OrderID and FDs: OrderID -> CustomerID and CustomerID -> CustomerCity. What normal form does this violate?",
        "options": [
            {"id": "a", "text": "Third Normal Form (3NF), because CustomerCity is transitively dependent on OrderID via CustomerID", "correct": True},
            {"id": "b", "text": "First Normal Form (1NF), because values are non-atomic", "correct": False, "maps_to": "D13", "misconception": "All columns contain atomic values, so 1NF is satisfied"},
            {"id": "c", "text": "Second Normal Form (2NF), because of partial dependencies", "correct": False, "maps_to": "D13", "misconception": "The key is a single attribute OrderID, so partial dependencies are impossible"},
            {"id": "d", "text": "It satisfies all normal forms including BCNF", "correct": False, "maps_to": "D14", "misconception": "CustomerID is not a superkey, so BCNF and 3NF are violated"}
        ],
        "explanation": "OrderID -> CustomerCity is transitive via non-key CustomerID. This violates 3NF.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_A_04",
        "concept": "D13",
        "family": "A",
        "difficulty": 1,
        "prompt": "If a relation R has only single-attribute candidate keys (no composite keys) and is in 1NF, what is automatically true?",
        "options": [
            {"id": "a", "text": "R is automatically in Second Normal Form (2NF)", "correct": True},
            {"id": "b", "text": "R is automatically in Third Normal Form (3NF)", "correct": False, "maps_to": "D13", "misconception": "Transitive dependencies can still exist between non-prime attributes"},
            {"id": "c", "text": "R is automatically in BCNF", "correct": False, "maps_to": "D14", "misconception": "Single attribute keys do not eliminate transitive dependencies"},
            {"id": "d", "text": "R cannot have foreign keys", "correct": False, "maps_to": "D04", "misconception": "Normal forms do not restrict foreign key presence"}
        ],
        "explanation": "Partial dependency requires a proper subset of a composite key. If all candidate keys are single attributes, partial dependencies cannot exist, making it 2NF.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_A_05",
        "concept": "D13",
        "family": "A",
        "difficulty": 3,
        "prompt": "What is an Insertion Anomaly in an unnormalized relational schema?",
        "options": [
            {"id": "a", "text": "Inability to record certain facts without artificially inserting unrelated facts (e.g. cannot record a new course without enrolling a student)", "correct": True},
            {"id": "b", "text": "Disk failure during an INSERT statement", "correct": False, "maps_to": "D15", "misconception": "Confuses schema anomalies with physical disk drive crashes"},
            {"id": "c", "text": "Failure to insert because a primary key was provided", "correct": False, "maps_to": "D03", "misconception": "Primary keys facilitate insertions, not block them"},
            {"id": "d", "text": "Inserting duplicate rows into a multiset", "correct": False, "maps_to": "D02", "misconception": "Anomalies refer to logical schema design flaws, not intentional multisets"}
        ],
        "explanation": "An insertion anomaly occurs when dependent information cannot be stored without prematurely inserting dummy or null values for unrelated entities.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_A_06",
        "concept": "D13",
        "family": "A",
        "difficulty": 2,
        "prompt": "Which of the following conditions satisfies Third Normal Form (3NF) for every non-trivial functional dependency X -> Y in relation R?",
        "options": [
            {"id": "a", "text": "Either X is a superkey of R, OR Y is a prime attribute (part of some candidate key)", "correct": True},
            {"id": "b", "text": "X must always be a candidate key, with no exceptions", "correct": False, "maps_to": "D14", "misconception": "This is the stricter definition of BCNF, not 3NF"},
            {"id": "c", "text": "Y must be a foreign key in another table", "correct": False, "maps_to": "D04", "misconception": "3NF definition has no requirement that Y be a foreign key"},
            {"id": "d", "text": "X and Y must be identical attributes", "correct": False, "maps_to": "D12", "misconception": "Identical attributes form a trivial dependency, not the 3NF condition"}
        ],
        "explanation": "3NF relaxes BCNF by permitting X -> Y if Y is a prime attribute (part of a candidate key), even if X is not a superkey.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_B_01",
        "concept": "D13",
        "family": "B",
        "difficulty": 1,
        "prompt": "A student database stores hobbies as 'Chess, Swimming, Reading' inside a single column 'Hobbies'. Why does this violate 1NF?",
        "options": [
            {"id": "a", "text": "The values in 'Hobbies' are multivalued (non-atomic)", "correct": True},
            {"id": "b", "text": "Hobbies is a foreign key without a primary key", "correct": False, "maps_to": "D04", "misconception": "The issue is column value atomicity, not referential keys"},
            {"id": "c", "text": "A student cannot participate in more than two hobbies", "correct": False, "maps_to": "D13", "misconception": "Arbitrary domain rule that has nothing to do with relational theory"},
            {"id": "d", "text": "The hobbies column is not sorted alphabetically", "correct": False, "maps_to": "D08", "misconception": "Sorting has nothing to do with normalization"}
        ],
        "explanation": "First Normal Form requires attribute domains to be atomic. Storing comma-separated lists violates value atomicity.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_B_02",
        "concept": "D13",
        "family": "B",
        "difficulty": 2,
        "prompt": "Given relation StudentCourse(StudentID, CourseID, StudentName, Grade) where {StudentID, CourseID} is the primary key and StudentID -> StudentName holds. What normal form violation is present?",
        "options": [
            {"id": "a", "text": "Violation of 2NF due to partial dependency (StudentName depends on part of the composite key)", "correct": True},
            {"id": "b", "text": "Violation of 1NF due to non-atomic values", "correct": False, "maps_to": "D13", "misconception": "Attributes are scalar and atomic"},
            {"id": "c", "text": "Violation of 3NF only, but 2NF is satisfied", "correct": False, "maps_to": "D13", "misconception": "Partial dependency violates 2NF before 3NF can even be considered"},
            {"id": "d", "text": "No violation; the relation is in BCNF", "correct": False, "maps_to": "D14", "misconception": "StudentID is a proper subset of the key, violating 2NF, 3NF, and BCNF"}
        ],
        "explanation": "StudentName depends on StudentID, which is a proper subset of the composite candidate key {StudentID, CourseID}. This is a partial dependency violating 2NF.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_B_03",
        "concept": "D13",
        "family": "B",
        "difficulty": 2,
        "prompt": "What is a Deletion Anomaly in an unnormalized schema?",
        "options": [
            {"id": "a", "text": "Deleting one fact unintentionally loses another critical, unrelated fact (e.g. deleting the last student in a department deletes all department details)", "correct": True},
            {"id": "b", "text": "The DELETE command causes a database server crash", "correct": False, "maps_to": "D15", "misconception": "Confuses logical schema anomalies with software crashes"},
            {"id": "c", "text": "Accidental deletion of all foreign key constraints", "correct": False, "maps_to": "D04", "misconception": "Constraints are not dropped by row deletions"},
            {"id": "d", "text": "Inability to delete rows that contain NULL values", "correct": False, "maps_to": "D08", "misconception": "Rows with NULLs can be deleted like any other rows"}
        ],
        "explanation": "A deletion anomaly occurs when removing an instance of one entity causes unintended loss of information about another entity.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_B_04",
        "concept": "D13",
        "family": "B",
        "difficulty": 3,
        "prompt": "How is a transitive dependency X -> Z eliminated when decomposing relation R(X, Y, Z) into 3NF?",
        "options": [
            {"id": "a", "text": "Decompose R into R1(X, Y) and R2(Y, Z)", "correct": True},
            {"id": "b", "text": "Decompose R into R1(X, Z) and R2(Y)", "correct": False, "maps_to": "D13", "misconception": "Loses the dependency X -> Y and isolates Y"},
            {"id": "c", "text": "Add a new surrogate key W and drop column Y", "correct": False, "maps_to": "D03", "misconception": "Dropping columns results in loss of data"},
            {"id": "d", "text": "Merge R with another relation to form a wider table", "correct": False, "maps_to": "D13", "misconception": "Denormalization increases anomalies rather than eliminating them"}
        ],
        "explanation": "Standard 3NF synthesis decomposes R(X, Y, Z) where X -> Y and Y -> Z into R1(X, Y) and R2(Y, Z), removing the transitive dependency.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D13_B_05",
        "concept": "D13",
        "family": "B",
        "difficulty": 1,
        "prompt": "Why do relational designers normalize tables instead of keeping all enterprise data in a single massive universal table?",
        "options": [
            {"id": "a", "text": "To minimize data redundancy and prevent insertion, update, and deletion anomalies", "correct": True},
            {"id": "b", "text": "To reduce the number of foreign keys to zero", "correct": False, "maps_to": "D04", "misconception": "Normalization actually increases the number of normalized tables and foreign keys"},
            {"id": "c", "text": "To eliminate the need for SQL queries", "correct": False, "maps_to": "D08", "misconception": "Normalized schemas are queried extensively with SQL joins"},
            {"id": "d", "text": "To allow tables to bypass primary key constraints", "correct": False, "maps_to": "D03", "misconception": "Every normalized table requires a primary key"}
        ],
        "explanation": "Normalization organizes data into focused tables, eliminating redundant storage and guaranteeing data integrity against modification anomalies.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D14: BCNF and Decomposition (11 questions)
    # ==========================================
    {
        "id": "Q_D14_A_01",
        "concept": "D14",
        "family": "A",
        "difficulty": 1,
        "prompt": "What is the defining condition for a relation schema R to be in Boyce-Codd Normal Form (BCNF)?",
        "options": [
            {"id": "a", "text": "For every non-trivial functional dependency X -> Y, X must be a superkey of R", "correct": True},
            {"id": "b", "text": "For every functional dependency X -> Y, Y must be a prime attribute", "correct": False, "maps_to": "D13", "misconception": "This is part of the 3NF condition, not BCNF"},
            {"id": "c", "text": "The relation must have no foreign keys", "correct": False, "maps_to": "D04", "misconception": "BCNF relations routinely possess foreign keys"},
            {"id": "d", "text": "All candidate keys must consist of exactly one attribute", "correct": False, "maps_to": "D03", "misconception": "BCNF permits composite candidate keys as long as the superkey condition holds"}
        ],
        "explanation": "BCNF strictly requires that the determinant (left-hand side X) of every non-trivial FD must be a superkey.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_A_02",
        "concept": "D14",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is the crucial difference between 3NF and BCNF?",
        "options": [
            {"id": "a", "text": "3NF allows X -> Y if Y is a prime attribute even when X is not a superkey; BCNF never permits this exception", "correct": True},
            {"id": "b", "text": "3NF applies to multiset tables, while BCNF applies only to set relations", "correct": False, "maps_to": "D02", "misconception": "Both normal forms apply to relational schema theory"},
            {"id": "c", "text": "BCNF allows partial dependencies while 3NF does not", "correct": False, "maps_to": "D13", "misconception": "BCNF is strictly stronger than 3NF; it forbids partial dependencies completely"},
            {"id": "d", "text": "3NF requires zero functional dependencies", "correct": False, "maps_to": "D12", "misconception": "All normal forms model schemas with functional dependencies"}
        ],
        "explanation": "3NF has an escape clause: if Y is prime, X does not need to be a superkey. BCNF eliminates this exception, making it strictly stronger.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_A_03",
        "concept": "D14",
        "family": "A",
        "difficulty": 2,
        "prompt": "What defines a Lossless-Join Decomposition of relation R into R1 and R2?",
        "options": [
            {"id": "a", "text": "Natural join of R1 and R2 produces exactly the original relation R with no spurious tuples: π_R1(R) ⋈ π_R2(R) = R", "correct": True},
            {"id": "b", "text": "The sum of attributes in R1 and R2 is smaller than R", "correct": False, "maps_to": "D14", "misconception": "Decomposition attributes must cover all original attributes"},
            {"id": "c", "text": "No foreign key constraints are needed", "correct": False, "maps_to": "D04", "misconception": "Lossless joins rely on key matches across decomposed parts"},
            {"id": "d", "text": "Both R1 and R2 have zero duplicate rows", "correct": False, "maps_to": "D02", "misconception": "Describes set property, not lossless join guarantee"}
        ],
        "explanation": "A decomposition is lossless if joining the decomposed tables reconstructs the exact original relation without creating false (spurious) tuples.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_A_04",
        "concept": "D14",
        "family": "A",
        "difficulty": 3,
        "prompt": "Which test mathematically guarantees that a binary decomposition of R into R1 and R2 is lossless?",
        "options": [
            {"id": "a", "text": "(R1 ∩ R2) -> R1 OR (R1 ∩ R2) -> R2 must hold in F+ (the common attribute must be a superkey of at least one relation)", "correct": True},
            {"id": "b", "text": "R1 and R2 must have zero common attributes (R1 ∩ R2 = ∅)", "correct": False, "maps_to": "D14", "misconception": "Disjoint attribute sets cause a Cartesian product, producing massive spurious tuples"},
            {"id": "c", "text": "R1 must have strictly more tuples than R2", "correct": False, "maps_to": "D14", "misconception": "Row count has no bearing on schema-level lossless join property"},
            {"id": "d", "text": "Both R1 and R2 must be in 1NF only", "correct": False, "maps_to": "D13", "misconception": "1NF does not guarantee lossless reconstruction"}
        ],
        "explanation": "A binary decomposition is lossless if and only if the shared attributes (R1 ∩ R2) functionally determine all attributes of R1 or all attributes of R2.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_A_05",
        "concept": "D14",
        "family": "A",
        "difficulty": 3,
        "prompt": "What major trade-off can arise when decomposing a schema into BCNF compared to 3NF?",
        "options": [
            {"id": "a", "text": "BCNF decomposition is not always guaranteed to be dependency-preserving, whereas 3NF always guarantees both lossless-join and dependency preservation", "correct": True},
            {"id": "b", "text": "BCNF tables cannot be queried using SQL SELECT", "correct": False, "maps_to": "D08", "misconception": "All relational schemas are queryable with SQL"},
            {"id": "c", "text": "BCNF causes disk files to expand by 500%", "correct": False, "maps_to": "D01", "misconception": "Normalization reduces redundancy, typically saving space"},
            {"id": "d", "text": "BCNF forces all foreign keys to be disabled", "correct": False, "maps_to": "D04", "misconception": "Foreign keys are central to normalized schemas"}
        ],
        "explanation": "While any schema can be decomposed into 3NF preserving all dependencies, achieving BCNF may sometimes sacrifice dependency preservation.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_A_06",
        "concept": "D14",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is Dependency Preservation in schema decomposition?",
        "options": [
            {"id": "a", "text": "The union of functional dependencies holding on each individual decomposed relation logically implies the entire original FD set: (F1 ∪ F2)+ = F+", "correct": True},
            {"id": "b", "text": "Every attribute remains in a single table", "correct": False, "maps_to": "D14", "misconception": "That describes no decomposition at all"},
            {"id": "c", "text": "Primary keys cannot be altered after table creation", "correct": False, "maps_to": "D03", "misconception": "Confuses key immutability with dependency preservation"},
            {"id": "d", "text": "All foreign key cascade actions are removed", "correct": False, "maps_to": "D04", "misconception": "Unrelated to functional dependency preservation"}
        ],
        "explanation": "Dependency preservation ensures all original functional dependencies can be enforced within individual tables without computing cross-table joins.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_B_01",
        "concept": "D14",
        "family": "B",
        "difficulty": 1,
        "prompt": "If a relation is in BCNF, which of the following is guaranteed to be true?",
        "options": [
            {"id": "a", "text": "It is also in 3NF, 2NF, and 1NF", "correct": True},
            {"id": "b", "text": "It contains zero primary keys", "correct": False, "maps_to": "D03", "misconception": "Every relational table requires a primary key"},
            {"id": "c", "text": "It can have no functional dependencies whatsoever", "correct": False, "maps_to": "D12", "misconception": "BCNF relations have functional dependencies whose determinants are superkeys"},
            {"id": "d", "text": "It cannot be decomposed any further", "correct": False, "maps_to": "D14", "misconception": "Tables can be further decomposed for 4NF or 5NF if multivalued dependencies exist"}
        ],
        "explanation": "The normal forms form a strict hierarchy: BCNF ⊂ 3NF ⊂ 2NF ⊂ 1NF. Any relation in BCNF is automatically in 3NF, 2NF, and 1NF.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_B_02",
        "concept": "D14",
        "family": "B",
        "difficulty": 2,
        "prompt": "Given relation R(A, B, C) where candidate keys are {A, B} and {B, C}, and FD C -> A holds. Is R in 3NF, and is R in BCNF?",
        "options": [
            {"id": "a", "text": "In 3NF (because A is prime), but NOT in BCNF (because C is not a superkey)", "correct": True},
            {"id": "b", "text": "In BCNF, but not in 3NF", "correct": False, "maps_to": "D14", "misconception": "BCNF is strictly stronger than 3NF; it is impossible to be in BCNF without being in 3NF"},
            {"id": "c", "text": "In neither 3NF nor BCNF", "correct": False, "maps_to": "D13", "misconception": "Fails to recognize that A is a prime attribute, which satisfies 3NF"},
            {"id": "d", "text": "In both 3NF and BCNF", "correct": False, "maps_to": "D14", "misconception": "C is not a superkey, which violates BCNF"}
        ],
        "explanation": "In C -> A, A is part of candidate key {A, B} (so A is prime), satisfying 3NF. But C is not a superkey, so BCNF is violated.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_B_03",
        "concept": "D14",
        "family": "B",
        "difficulty": 2,
        "prompt": "What happens if a decomposition is NOT lossless (lossy)?",
        "options": [
            {"id": "a", "text": "Rejoining the decomposed tables generates spurious (invalid) tuples that were not in the original relation", "correct": True},
            {"id": "b", "text": "The database immediately crashes with a segmentation fault", "correct": False, "maps_to": "D01", "misconception": "Lossy join is a logical data anomaly, not an operating system crash"},
            {"id": "c", "text": "All data in the tables is permanently erased", "correct": False, "maps_to": "D15", "misconception": "Data is not deleted; phantom records are created on re-join"},
            {"id": "d", "text": "No queries can ever be written against the decomposed tables", "correct": False, "maps_to": "D08", "misconception": "Tables can be queried, but joins yield inaccurate results"}
        ],
        "explanation": "A lossy decomposition causes spurious tuples when tables are joined back together, misrepresenting true facts.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_B_04",
        "concept": "D14",
        "family": "B",
        "difficulty": 3,
        "prompt": "Given relation R(A, B, C) with FD A -> B. If we decompose R into R1(A, B) and R2(A, C), is this decomposition lossless?",
        "options": [
            {"id": "a", "text": "Yes, because the common attribute A is a superkey of R1 (A -> B holds)", "correct": True},
            {"id": "b", "text": "No, because C is not included in R1", "correct": False, "maps_to": "D14", "misconception": "C is present in R2, so all attributes are preserved"},
            {"id": "c", "text": "No, because binary decompositions can never be lossless", "correct": False, "maps_to": "D14", "misconception": "Binary decompositions are frequently lossless when common attributes form a key"},
            {"id": "d", "text": "Only if table R contains fewer than 10 rows", "correct": False, "maps_to": "D14", "misconception": "Lossless join property is independent of instance cardinality"}
        ],
        "explanation": "R1 ∩ R2 = {A}. Since A -> B holds, {A}+ contains all attributes of R1, proving the decomposition is lossless.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D14_B_05",
        "concept": "D14",
        "family": "B",
        "difficulty": 1,
        "prompt": "Why might a database architect deliberately choose to retain a 3NF design instead of decomposing into BCNF?",
        "options": [
            {"id": "a", "text": "To preserve a functional dependency that would be lost during BCNF decomposition, avoiding expensive cross-table join validation", "correct": True},
            {"id": "b", "text": "Because BCNF tables do not support integer columns", "correct": False, "maps_to": "D02", "misconception": "Data types are unaffected by normal form choices"},
            {"id": "c", "text": "Because 3NF tables execute queries with zero CPU usage", "correct": False, "maps_to": "D18", "misconception": "Unrealistic performance fantasy"},
            {"id": "d", "text": "Because BCNF is obsolete and replaced by NoSQL", "correct": False, "maps_to": "D01", "misconception": "BCNF remains a foundational relational standard"}
        ],
        "explanation": "When BCNF decomposition cannot preserve all functional dependencies, architects often stay in 3NF so dependencies can be checked efficiently on single tables.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D15: Transactions and ACID (11 questions)
    # ==========================================
    {
        "id": "Q_D15_A_01",
        "concept": "D15",
        "family": "A",
        "difficulty": 1,
        "prompt": "Which ACID property guarantees that all operations of a transaction complete successfully or none of them take effect (all-or-nothing)?",
        "options": [
            {"id": "a", "text": "Atomicity", "correct": True},
            {"id": "b", "text": "Consistency", "correct": False, "maps_to": "D15", "misconception": "Consistency ensures the database transitions between valid states preserving invariants"},
            {"id": "c", "text": "Isolation", "correct": False, "maps_to": "D15", "misconception": "Isolation ensures concurrent transactions execute without interfering with each other"},
            {"id": "d", "text": "Durability", "correct": False, "maps_to": "D15", "misconception": "Durability ensures committed updates persist through crashes"}
        ],
        "explanation": "Atomicity ensures that a transaction is treated as a single indivisible unit: either all statements commit, or the entire transaction is rolled back.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_A_02",
        "concept": "D15",
        "family": "A",
        "difficulty": 2,
        "prompt": "A transaction transfers $100 from Account A to Account B. What does Consistency require in this scenario?",
        "options": [
            {"id": "a", "text": "The total sum of balances in A and B must remain unchanged before and after the transaction completes", "correct": True},
            {"id": "b", "text": "Account A must be locked for 24 hours", "correct": False, "maps_to": "D16", "misconception": "Excessive locking duration has nothing to do with consistency invariants"},
            {"id": "c", "text": "The transfer must complete within 1 microsecond", "correct": False, "maps_to": "D15", "misconception": "ACID properties specify correctness guarantees, not speed thresholds"},
            {"id": "d", "text": "No other user may read Account C during the transfer", "correct": False, "maps_to": "D16", "misconception": "Irrelevant locking of unrelated accounts"}
        ],
        "explanation": "Consistency guarantees that execution of a transaction preserves all database integrity constraints and business invariants.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_A_03",
        "concept": "D15",
        "family": "A",
        "difficulty": 2,
        "prompt": "What does Durability guarantee in the event of a sudden power outage immediately after a transaction executes COMMIT?",
        "options": [
            {"id": "a", "text": "All changes made by the committed transaction survive the crash and are restored upon database restart", "correct": True},
            {"id": "b", "text": "The transaction is rolled back because the system rebooted", "correct": False, "maps_to": "D15", "misconception": "Committed transactions must never be rolled back upon recovery; uncommitted ones are"},
            {"id": "c", "text": "The entire database is reverted to its state from one year ago", "correct": False, "maps_to": "D15", "misconception": "Gross exaggeration of crash recovery"},
            {"id": "d", "text": "Only in-memory read operations are restored", "correct": False, "maps_to": "D15", "misconception": "Durability specifically protects committed write modifications"}
        ],
        "explanation": "Durability guarantees that once a transaction commits, its modifications are permanently recorded (e.g. via write-ahead logging) and persist across system failures.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_A_04",
        "concept": "D15",
        "family": "A",
        "difficulty": 1,
        "prompt": "What SQL command explicitly cancels all uncommitted modifications made during the current transaction?",
        "options": [
            {"id": "a", "text": "ROLLBACK", "correct": True},
            {"id": "b", "text": "COMMIT", "correct": False, "maps_to": "D15", "misconception": "COMMIT makes changes permanent, the exact opposite of ROLLBACK"},
            {"id": "c", "text": "DROP", "correct": False, "maps_to": "D08", "misconception": "DROP deletes schema objects like tables"},
            {"id": "d", "text": "ABORT_CLUSTER", "correct": False, "maps_to": "D15", "misconception": "Invented non-standard command"}
        ],
        "explanation": "ROLLBACK discards all modifications made since the beginning of the transaction (or back to a SAVEPOINT).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_A_05",
        "concept": "D15",
        "family": "A",
        "difficulty": 3,
        "prompt": "What role does the Write-Ahead Logging (WAL) protocol play in providing Atomicity and Durability?",
        "options": [
            {"id": "a", "text": "Log records describing data changes must be written to non-volatile disk before the corresponding dirty data pages are written to disk", "correct": True},
            {"id": "b", "text": "All SQL queries must be printed to terminal console before compilation", "correct": False, "maps_to": "D01", "misconception": "WAL refers to disk transaction logging, not console output"},
            {"id": "c", "text": "Database backups must be created ahead of every SELECT query", "correct": False, "maps_to": "D15", "misconception": "Backups ahead of queries would destroy performance and is not WAL"},
            {"id": "d", "text": "Transactions must write their data directly to client memory", "correct": False, "maps_to": "D01", "misconception": "Confuses server-side disk persistence with client memory"}
        ],
        "explanation": "WAL requires that log records (undo and redo info) reach disk before data pages, ensuring changes can be undone (Atomicity) or redone (Durability) during recovery.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_A_06",
        "concept": "D15",
        "family": "A",
        "difficulty": 2,
        "prompt": "In the standard transaction state diagram, what state does a transaction enter immediately after executing its final statement but before writing the commit record?",
        "options": [
            {"id": "a", "text": "Partially Committed", "correct": True},
            {"id": "b", "text": "Committed", "correct": False, "maps_to": "D15", "misconception": "Committed is entered only after the commit record is successfully persisted to disk"},
            {"id": "c", "text": "Failed", "correct": False, "maps_to": "D15", "misconception": "Failed is entered if a normal execution or hardware fault occurs"},
            {"id": "d", "text": "Terminated", "correct": False, "maps_to": "D15", "misconception": "Terminated is the final state after leaving committed or aborted states"}
        ],
        "explanation": "A transaction enters the 'Partially Committed' state after its final statement executes; it transitions to 'Committed' once all log records are flushed to disk.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_B_01",
        "concept": "D15",
        "family": "B",
        "difficulty": 1,
        "prompt": "Which ACID property ensures that intermediate, incomplete results of concurrent transactions are hidden from other transactions?",
        "options": [
            {"id": "a", "text": "Isolation", "correct": True},
            {"id": "b", "text": "Durability", "correct": False, "maps_to": "D15", "misconception": "Durability relates to crash recovery, not concurrency visibility"},
            {"id": "c", "text": "Atomicity", "correct": False, "maps_to": "D15", "misconception": "Atomicity ensures all-or-nothing completion, not concurrency isolation"},
            {"id": "d", "text": "Consistency", "correct": False, "maps_to": "D15", "misconception": "Consistency ensures integrity rules are preserved"}
        ],
        "explanation": "Isolation prevents concurrent transactions from seeing each other's intermediate, uncommitted updates.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_B_02",
        "concept": "D15",
        "family": "B",
        "difficulty": 2,
        "prompt": "What is the function of a SAVEPOINT within a database transaction?",
        "options": [
            {"id": "a", "text": "It sets a marker allowing a transaction to be partially rolled back to that point without aborting the entire transaction", "correct": True},
            {"id": "b", "text": "It exports the table to an Excel spreadsheet", "correct": False, "maps_to": "D01", "misconception": "Savepoint is a transactional state marker, not an export feature"},
            {"id": "c", "text": "It commits the transaction permanently and starts a new one", "correct": False, "maps_to": "D15", "misconception": "Savepoints do not commit transactions"},
            {"id": "d", "text": "It creates a complete physical disk clone of the database", "correct": False, "maps_to": "D15", "misconception": "Confuses savepoints with database storage snapshots"}
        ],
        "explanation": "SAVEPOINT name creates a point within a transaction to which you can later rollback using ROLLBACK TO SAVEPOINT name.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_B_03",
        "concept": "D15",
        "family": "B",
        "difficulty": 2,
        "prompt": "If a transaction aborts before reaching its commit point, what must the DBMS recovery subsystem do?",
        "options": [
            {"id": "a", "text": "Undo all modifications made by the transaction to restore the database to its pre-transaction state", "correct": True},
            {"id": "b", "text": "Re-run the transaction automatically 10,000 times", "correct": False, "maps_to": "D15", "misconception": "The DBMS rolls back; automatic unbounded looping would freeze the system"},
            {"id": "c", "text": "Drop the tables that were modified", "correct": False, "maps_to": "D08", "misconception": "Tables are preserved; only row modifications are rolled back"},
            {"id": "d", "text": "Leave the partial changes in place and notify the user", "correct": False, "maps_to": "D15", "misconception": "Violates Atomicity (all-or-nothing guarantee)"}
        ],
        "explanation": "To maintain Atomicity, any changes written by an aborted transaction must be reversed (undone) using the undo log.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_B_04",
        "concept": "D15",
        "family": "B",
        "difficulty": 3,
        "prompt": "What is the purpose of database Checkpointing during write-ahead logging?",
        "options": [
            {"id": "a", "text": "To flush dirty data pages to disk and write a checkpoint record, bounding the log volume needed to scan during crash recovery", "correct": True},
            {"id": "b", "text": "To verify that all user passwords are encrypted", "correct": False, "maps_to": "D01", "misconception": "Checkpoints relate to disk write synchronization and recovery logs"},
            {"id": "c", "text": "To delete all index structures to reclaim storage", "correct": False, "maps_to": "D17", "misconception": "Checkpoints never delete table indexes"},
            {"id": "d", "text": "To lock all tables indefinitely until reboot", "correct": False, "maps_to": "D16", "misconception": "Checkpoints are routine background operations, not permanent table freezes"}
        ],
        "explanation": "Checkpoints write cached dirty pages to disk so that upon restart, the recovery manager does not need to scan the entire log from the system's creation.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D15_B_05",
        "concept": "D15",
        "family": "B",
        "difficulty": 1,
        "prompt": "Which component of the DBMS is primarily responsible for ensuring the Durability and Atomicity of transactions?",
        "options": [
            {"id": "a", "text": "Recovery Manager", "correct": True},
            {"id": "b", "text": "Query Optimizer", "correct": False, "maps_to": "D18", "misconception": "Query Optimizer generates efficient execution plans"},
            {"id": "c", "text": "HTML Form Renderer", "correct": False, "maps_to": "D01", "misconception": "Client presentation layer"},
            {"id": "d", "text": "Parser and Lexer", "correct": False, "maps_to": "D18", "misconception": "Parser validates SQL grammar and syntax"}
        ],
        "explanation": "The Recovery Manager uses logging and checkpointing mechanisms to guarantee Atomicity and Durability.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D16: Concurrency Control (11 questions)
    # ==========================================
    {
        "id": "Q_D16_A_01",
        "concept": "D16",
        "family": "A",
        "difficulty": 1,
        "prompt": "What concurrency phenomenon occurs when Transaction T1 reads uncommitted changes made by Transaction T2, and T2 subsequently rolls back?",
        "options": [
            {"id": "a", "text": "Dirty Read", "correct": True},
            {"id": "b", "text": "Non-Repeatable Read", "correct": False, "maps_to": "D16", "misconception": "Non-repeatable read occurs when committed updates change row values between reads"},
            {"id": "c", "text": "Phantom Read", "correct": False, "maps_to": "D16", "misconception": "Phantom read occurs when committed inserts/deletes alter the row count of a range query"},
            {"id": "d", "text": "Lost Update", "correct": False, "maps_to": "D16", "misconception": "Lost update occurs when two transactions overwrite each other's writes"}
        ],
        "explanation": "A Dirty Read happens when a transaction reads data modified by a concurrent uncommitted transaction that later aborts.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_A_02",
        "concept": "D16",
        "family": "A",
        "difficulty": 2,
        "prompt": "Which ANSI SQL isolation level prevents both Dirty Reads and Non-Repeatable Reads, but may still permit Phantom Reads?",
        "options": [
            {"id": "a", "text": "Repeatable Read", "correct": True},
            {"id": "b", "text": "Read Committed", "correct": False, "maps_to": "D16", "misconception": "Read Committed prevents Dirty Reads, but permits Non-Repeatable Reads"},
            {"id": "c", "text": "Serializable", "correct": False, "maps_to": "D16", "misconception": "Serializable prevents all concurrency anomalies including Phantom Reads"},
            {"id": "d", "text": "Read Uncommitted", "correct": False, "maps_to": "D16", "misconception": "Read Uncommitted allows Dirty Reads"}
        ],
        "explanation": "Repeatable Read guarantees that any row read during the transaction yields the same value upon re-reading, but new matching rows (phantoms) may appear.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_A_03",
        "concept": "D16",
        "family": "A",
        "difficulty": 2,
        "prompt": "What rule governs the Two-Phase Locking (2PL) protocol to guarantee serializability?",
        "options": [
            {"id": "a", "text": "Once a transaction releases any lock (shrinking phase), it cannot acquire any new locks (growing phase is over)", "correct": True},
            {"id": "b", "text": "All transactions must execute in under two seconds", "correct": False, "maps_to": "D16", "misconception": "2PL is a locking protocol, not a time limit"},
            {"id": "c", "text": "A transaction must lock the entire database before reading any row", "correct": False, "maps_to": "D16", "misconception": "2PL works with fine-grained granular locks"},
            {"id": "d", "text": "Transactions must acquire locks only on Tuesdays and Thursdays", "correct": False, "maps_to": "D16", "misconception": "Absurd timing rule"}
        ],
        "explanation": "2PL divides execution into a Growing Phase (only acquiring locks) and a Shrinking Phase (only releasing locks). No lock may be acquired after releasing any lock.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_A_04",
        "concept": "D16",
        "family": "A",
        "difficulty": 3,
        "prompt": "How does Strict 2PL differ from standard basic 2PL?",
        "options": [
            {"id": "a", "text": "Strict 2PL holds all exclusive (write) locks until the transaction commits or aborts, preventing cascading rollbacks", "correct": True},
            {"id": "b", "text": "Strict 2PL never permits concurrent read operations", "correct": False, "maps_to": "D16", "misconception": "Shared read locks can still be shared concurrently"},
            {"id": "c", "text": "Strict 2PL completely eliminates deadlocks", "correct": False, "maps_to": "D16", "misconception": "Strict 2PL can still encounter deadlocks and requires deadlock detection"},
            {"id": "d", "text": "Strict 2PL requires all data to be stored in RAM", "correct": False, "maps_to": "D01", "misconception": "Locking protocols are storage-engine agnostic"}
        ],
        "explanation": "Strict 2PL holds all exclusive locks until transaction completion, preventing other transactions from reading uncommitted data and eliminating cascading rollbacks.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_A_05",
        "concept": "D16",
        "family": "A",
        "difficulty": 2,
        "prompt": "In a precedence (serialization) graph for concurrency control, what indicates that a schedule is Conflict Serializable?",
        "options": [
            {"id": "a", "text": "The graph contains no cycles (it is a Directed Acyclic Graph - DAG)", "correct": True},
            {"id": "b", "text": "The graph contains at least three closed loops", "correct": False, "maps_to": "D16", "misconception": "Cycles in the precedence graph signify non-serializable schedules"},
            {"id": "c", "text": "Every node has in-degree equal to out-degree", "correct": False, "maps_to": "D16", "misconception": "Eulerian circuit criteria is not relevant to serializability"},
            {"id": "d", "text": "All transactions commit at the exact same millisecond", "correct": False, "maps_to": "D15", "misconception": "Simultaneous commit is not related to conflict serializability"}
        ],
        "explanation": "A schedule is conflict serializable if and only if its precedence (conflict) graph contains no cycles (is a DAG).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_A_06",
        "concept": "D16",
        "family": "A",
        "difficulty": 3,
        "prompt": "In deadlock prevention, how does the 'Wait-Die' non-preemptive scheme behave when transaction Ti requests a lock held by Tj?",
        "options": [
            {"id": "a", "text": "If Ti is older than Tj, Ti is allowed to wait; if Ti is younger than Tj, Ti dies (is aborted and restarted)", "correct": True},
            {"id": "b", "text": "If Ti is younger than Tj, Ti preempts Tj; otherwise Ti dies", "correct": False, "maps_to": "D16", "misconception": "Describes the Wound-Wait scheme"},
            {"id": "c", "text": "Both Ti and Tj are immediately terminated", "correct": False, "maps_to": "D16", "misconception": "Deadlock prevention targets only one transaction"},
            {"id": "d", "text": "Tj is forced to commit immediately without running remaining statements", "correct": False, "maps_to": "D15", "misconception": "Premature commit violates atomicity"}
        ],
        "explanation": "Wait-Die: older transactions may wait for younger ones, but younger transactions requesting locks held by older ones immediately die (abort).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_B_01",
        "concept": "D16",
        "family": "B",
        "difficulty": 1,
        "prompt": "What concurrency phenomenon occurs when Transaction T1 reads a row, Transaction T2 updates that row and commits, and T1 re-reads the row obtaining different values?",
        "options": [
            {"id": "a", "text": "Non-Repeatable Read (Fuzzy Read)", "correct": True},
            {"id": "b", "text": "Dirty Read", "correct": False, "maps_to": "D16", "misconception": "Dirty Read involves uncommitted data; here T2 committed"},
            {"id": "c", "text": "Phantom Read", "correct": False, "maps_to": "D16", "misconception": "Phantom Read involves newly inserted rows in range queries, not modifying an existing row"},
            {"id": "d", "text": "Deadlock Exception", "correct": False, "maps_to": "D16", "misconception": "No mutual lock blocking occurred"}
        ],
        "explanation": "A Non-Repeatable Read occurs when a transaction reads the same row twice and observes different data because a concurrent transaction updated it in between.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_B_02",
        "concept": "D16",
        "family": "B",
        "difficulty": 2,
        "prompt": "What concurrency phenomenon occurs when T1 queries all students with GPA > 3.5 (getting 10 rows), T2 inserts a new student with GPA 3.8 and commits, and T1 re-executes the query getting 11 rows?",
        "options": [
            {"id": "a", "text": "Phantom Read", "correct": True},
            {"id": "b", "text": "Dirty Read", "correct": False, "maps_to": "D16", "misconception": "T2 committed, so the data is not dirty"},
            {"id": "c", "text": "Non-Repeatable Read", "correct": False, "maps_to": "D16", "misconception": "Existing rows were not changed; a new row appeared (phantom)"},
            {"id": "d", "text": "Write-Skew Exception", "correct": False, "maps_to": "D16", "misconception": "Write-skew involves overlapping multi-key writes in snapshot isolation"}
        ],
        "explanation": "A Phantom Read occurs when rows matching a search condition change in count between reads due to concurrent inserts or deletes.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_B_03",
        "concept": "D16",
        "family": "B",
        "difficulty": 2,
        "prompt": "What condition constitutes a Deadlock between two transactions T1 and T2?",
        "options": [
            {"id": "a", "text": "T1 is waiting for a lock held by T2, and T2 is waiting for a lock held by T1, creating a circular wait", "correct": True},
            {"id": "b", "text": "Both transactions attempt to read the same row using shared locks", "correct": False, "maps_to": "D16", "misconception": "Shared locks are compatible and do not block each other"},
            {"id": "c", "text": "Both transactions commit at the exact same millisecond", "correct": False, "maps_to": "D15", "misconception": "Simultaneous commit is normal operation, not a deadlock"},
            {"id": "d", "text": "T1 aborts due to an arithmetic divide-by-zero error", "correct": False, "maps_to": "D08", "misconception": "Arithmetic errors abort individual statements without deadlock"}
        ],
        "explanation": "A Deadlock is a situation where each transaction in a cycle is waiting for a resource locked by another, preventing all from proceeding.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_B_04",
        "concept": "D16",
        "family": "B",
        "difficulty": 3,
        "prompt": "In deadlock prevention, how does the 'Wound-Wait' preemptive scheme behave when transaction Ti requests a lock held by Tj?",
        "options": [
            {"id": "a", "text": "If Ti is older than Tj, Ti wounds (preempts/aborts) Tj; if Ti is younger than Tj, Ti is permitted to wait", "correct": True},
            {"id": "b", "text": "If Ti is older than Tj, Ti waits; if Ti is younger, Ti dies", "correct": False, "maps_to": "D16", "misconception": "Describes the Wait-Die scheme"},
            {"id": "c", "text": "The transaction with fewer rows is always dropped", "correct": False, "maps_to": "D16", "misconception": "Schemes rely on transaction timestamps, not row counts"},
            {"id": "d", "text": "Both transactions are forced to downgrade to dirty read isolation", "correct": False, "maps_to": "D16", "misconception": "Isolation levels cannot be silently downgraded by the engine"}
        ],
        "explanation": "Wound-Wait: older transactions preempt ('wound') younger ones to acquire locks without waiting; younger transactions wait for older ones.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D16_B_05",
        "concept": "D16",
        "family": "B",
        "difficulty": 1,
        "prompt": "Which SQL isolation level provides the strongest concurrency guarantee, preventing all race conditions and anomalies?",
        "options": [
            {"id": "a", "text": "Serializable", "correct": True},
            {"id": "b", "text": "Repeatable Read", "correct": False, "maps_to": "D16", "misconception": "Repeatable Read can permit phantom reads"},
            {"id": "c", "text": "Read Committed", "correct": False, "maps_to": "D16", "misconception": "Read Committed permits non-repeatable reads and phantoms"},
            {"id": "d", "text": "Read Uncommitted", "correct": False, "maps_to": "D16", "misconception": "Read Uncommitted permits dirty reads"}
        ],
        "explanation": "SERIALIZABLE guarantees that execution of concurrent transactions yields the same state as some serial execution.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D17: Indexing (B+ trees) (12 questions)
    # ==========================================
    {
        "id": "Q_D17_A_01",
        "concept": "D17",
        "family": "A",
        "difficulty": 1,
        "prompt": "Why are B+ Trees predominantly preferred over standard binary search trees (BST) for disk-based database indexing?",
        "options": [
            {"id": "a", "text": "B+ Trees have a high branching factor (fan-out) that drastically reduces tree height and minimizes disk I/O operations", "correct": True},
            {"id": "b", "text": "Binary search trees cannot store integer keys", "correct": False, "maps_to": "D17", "misconception": "BSTs store integers easily; the issue is height and disk page locality"},
            {"id": "c", "text": "B+ Trees do not require balanced subtrees", "correct": False, "maps_to": "D17", "misconception": "B+ Trees are strictly balanced; all leaf nodes are at identical depth"},
            {"id": "d", "text": "Binary search trees are restricted strictly to RAM caches", "correct": False, "maps_to": "D17", "misconception": "BSTs can be placed on disk, but produce terrible I/O latency"}
        ],
        "explanation": "Each B+ tree node fits into a disk block with hundreds of keys (high fanout), keeping tree height low (typically 3-4) and minimizing disk seeks.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_A_02",
        "concept": "D17",
        "family": "A",
        "difficulty": 1,
        "prompt": "What structural feature of B+ Trees makes range queries (e.g. WHERE age BETWEEN 25 AND 35) exceptionally efficient?",
        "options": [
            {"id": "a", "text": "All leaf nodes are linked sequentially via pointers in a doubly-linked list", "correct": True},
            {"id": "b", "text": "Internal nodes store all data records directly", "correct": False, "maps_to": "D17", "misconception": "Internal nodes only store routing keys, not data records"},
            {"id": "c", "text": "Range queries bypass the index and scan the raw disk", "correct": False, "maps_to": "D17", "misconception": "B+ tree leaf traversal avoids raw table scans"},
            {"id": "d", "text": "B+ Trees maintain hash maps for every number range", "correct": False, "maps_to": "D17", "misconception": "Hash maps cannot efficiently support range queries"}
        ],
        "explanation": "In a B+ Tree, leaf nodes contain all data keys and are linked sequentially, allowing range scans to traverse leaves horizontally without re-navigating from the root.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_A_03",
        "concept": "D17",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is the key difference between a Clustered (Primary) Index and an Unclustered (Secondary) Index?",
        "options": [
            {"id": "a", "text": "A clustered index determines the physical storage ordering of table rows on disk; an unclustered index maintains pointers to data rows stored elsewhere", "correct": True},
            {"id": "b", "text": "A table can have ten clustered indexes, but only one unclustered index", "correct": False, "maps_to": "D17", "misconception": "A table can have at most ONE clustered index because physical rows can only have one physical order"},
            {"id": "c", "text": "Clustered indexes only work on string columns", "correct": False, "maps_to": "D17", "misconception": "Clustered indexes commonly index integer primary keys"},
            {"id": "d", "text": "Unclustered indexes do not store key values", "correct": False, "maps_to": "D17", "misconception": "Unclustered indexes store key values paired with row pointers"}
        ],
        "explanation": "Because physical disk records can only be ordered in one way, a table can possess only one clustered index. Secondary indexes store pointers to the table rows.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_A_04",
        "concept": "D17",
        "family": "A",
        "difficulty": 2,
        "prompt": "Given a composite B+ Tree index on (LastName, FirstName). Which query CANNOT utilize this index effectively?",
        "options": [
            {"id": "a", "text": "SELECT * FROM Users WHERE FirstName = 'Alice'", "correct": True},
            {"id": "b", "text": "SELECT * FROM Users WHERE LastName = 'Smith'", "correct": False, "maps_to": "D17", "misconception": "This query matches the leftmost prefix and uses the index perfectly"},
            {"id": "c", "text": "SELECT * FROM Users WHERE LastName = 'Smith' AND FirstName = 'Alice'", "correct": False, "maps_to": "D17", "misconception": "Matches both indexed columns completely"},
            {"id": "d", "text": "SELECT * FROM Users WHERE LastName LIKE 'Sm%'", "correct": False, "maps_to": "D17", "misconception": "Prefix LIKE matching on the leftmost column can leverage the index range"}
        ],
        "explanation": "According to the Leftmost Prefix Rule, a composite index on (A, B) cannot be utilized by a query that filters solely on B without mentioning A.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_A_05",
        "concept": "D17",
        "family": "A",
        "difficulty": 3,
        "prompt": "What is a Covering Index in SQL query execution?",
        "options": [
            {"id": "a", "text": "An index that contains all the columns requested by a query, allowing the engine to satisfy the query entirely from the index without accessing table data pages", "correct": True},
            {"id": "b", "text": "An index that covers the entire hard drive surface", "correct": False, "maps_to": "D01", "misconception": "Confuses database covering indexes with physical disk capacity"},
            {"id": "c", "text": "An index that automatically encrypts all columns", "correct": False, "maps_to": "D01", "misconception": "Covering index is an optimization strategy, not encryption"},
            {"id": "d", "text": "An index created exclusively on foreign keys", "correct": False, "maps_to": "D04", "misconception": "Covering indexes can be built on any set of columns to satisfy queries"}
        ],
        "explanation": "An index scan becomes an Index-Only Scan (covering index) when all projected and filtered columns reside directly in the index node entries.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_A_06",
        "concept": "D17",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is a major performance drawback of creating too many indexes on a database table?",
        "options": [
            {"id": "a", "text": "INSERT, UPDATE, and DELETE operations become significantly slower because every index must be modified on write", "correct": True},
            {"id": "b", "text": "SELECT queries become strictly illegal", "correct": False, "maps_to": "D08", "misconception": "SELECT queries are accelerated by appropriate indexes, never made illegal"},
            {"id": "c", "text": "The database cannot support foreign keys", "correct": False, "maps_to": "D04", "misconception": "Foreign keys generally benefit from indexes"},
            {"id": "d", "text": "It forces the DBMS to drop the primary key constraint", "correct": False, "maps_to": "D03", "misconception": "Primary keys remain enforced regardless of index count"}
        ],
        "explanation": "Every write operation (INSERT/UPDATE/DELETE) must update all relevant secondary indexes, increasing disk I/O and locking overhead.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_B_01",
        "concept": "D17",
        "family": "B",
        "difficulty": 1,
        "prompt": "In a B+ Tree of order p, where are the actual data records (or record pointers) stored?",
        "options": [
            {"id": "a", "text": "Exclusively in the leaf nodes", "correct": True},
            {"id": "b", "text": "Exclusively in the root node", "correct": False, "maps_to": "D17", "misconception": "The root node only holds high-level routing search keys"},
            {"id": "c", "text": "Evenly distributed across all internal and leaf nodes", "correct": False, "maps_to": "D17", "misconception": "Describes a standard B-tree, not a B+ tree"},
            {"id": "d", "text": "In a separate volatile cache outside the tree", "correct": False, "maps_to": "D01", "misconception": "Data pointers are persistently recorded in B+ tree leaf pages"}
        ],
        "explanation": "In a B+ Tree (unlike a classic B-Tree), internal nodes hold only routing keys, while all data records/pointers reside strictly in the leaf nodes.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_B_02",
        "concept": "D17",
        "family": "B",
        "difficulty": 2,
        "prompt": "What distinguishes a Dense Index from a Sparse Index?",
        "options": [
            {"id": "a", "text": "A dense index has an index entry for every search key value in the file; a sparse index has index entries for only some values (e.g. one per block)", "correct": True},
            {"id": "b", "text": "A dense index contains compressed strings; a sparse index contains integers", "correct": False, "maps_to": "D17", "misconception": "Denseness refers to key coverage, not compression or data types"},
            {"id": "c", "text": "A sparse index is stored on tape storage", "correct": False, "maps_to": "D01", "misconception": "Sparse indices are stored on disk blocks alongside tables"},
            {"id": "d", "text": "Dense indexes cannot be searched using binary search", "correct": False, "maps_to": "D17", "misconception": "Both index types are searched using binary search"}
        ],
        "explanation": "A dense index contains an entry for every record/key. A sparse index contains entries only for anchor records (often one per disk block) and requires sorted records.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_B_03",
        "concept": "D17",
        "family": "B",
        "difficulty": 2,
        "prompt": "Can a Sparse Index be constructed on an unclustered (unsorted) data file?",
        "options": [
            {"id": "a", "text": "No, a sparse index requires the data file to be physically sorted on the search key to locate unindexed records within blocks", "correct": True},
            {"id": "b", "text": "Yes, sparse indexes work on any randomly organized file", "correct": False, "maps_to": "D17", "misconception": "Without sorted data, skipping records between entries makes finding missing keys impossible"},
            {"id": "c", "text": "Only if the table contains fewer than 5 columns", "correct": False, "maps_to": "D17", "misconception": "Column count has no relevance to index sparsity requirements"},
            {"id": "d", "text": "Only if the primary key is a UUID", "correct": False, "maps_to": "D03", "misconception": "Random UUIDs disperse records unpredictably"}
        ],
        "explanation": "Sparse indexing relies on physical ordering so the database can navigate to a block and scan sequentially. Unsorted files require dense indexing.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_B_04",
        "concept": "D17",
        "family": "B",
        "difficulty": 3,
        "prompt": "If a B+ Tree has a fan-out of 100 and a height of 3 (root at level 1, internal at level 2, leaves at level 3), approximately how many leaf pages can it index?",
        "options": [
            {"id": "a", "text": "Approximately 10,000 leaf pages (100^2)", "correct": True},
            {"id": "b", "text": "Approximately 300 leaf pages", "correct": False, "maps_to": "D17", "misconception": "Adds fanout across levels instead of exponentiating"},
            {"id": "c", "text": "1,000,000 leaf pages", "correct": False, "maps_to": "D17", "misconception": "Computes 100^3 (which would be height 4)"},
            {"id": "d", "text": "100 leaf pages", "correct": False, "maps_to": "D17", "misconception": "Computes height 2"}
        ],
        "explanation": "With fan-out 100, level 1 has 1 root pointing to 100 level 2 nodes. Each level 2 node points to 100 level 3 leaf nodes: 100 × 100 = 10,000 leaf pages.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_B_05",
        "concept": "D17",
        "family": "B",
        "difficulty": 1,
        "prompt": "How does a Hash Index compare to a B+ Tree Index regarding range queries (e.g. col >= 10 AND col <= 50)?",
        "options": [
            {"id": "a", "text": "Hash indexes do not support range queries efficiently because hash functions scatter consecutive values randomly across buckets", "correct": True},
            {"id": "b", "text": "Hash indexes are vastly superior to B+ trees for range queries", "correct": False, "maps_to": "D17", "misconception": "Hash indexes excel at point equality lookups (O(1)), not ranges"},
            {"id": "c", "text": "Both perform identically across all query types", "correct": False, "maps_to": "D17", "misconception": "Their performance characteristics diverge sharply on range scans"},
            {"id": "d", "text": "Hash indexes sort data in reverse alphabetical order", "correct": False, "maps_to": "D17", "misconception": "Hash buckets have no sorting order"}
        ],
        "explanation": "Hash indexes map keys through a hash function with pseudo-random distribution, making equality lookups O(1) but rendering range scans impossible without full table scans.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D17_B_06",
        "concept": "D17",
        "family": "B",
        "difficulty": 2,
        "prompt": "What happens when an insert into a B+ Tree leaf node exceeds the maximum capacity of that node?",
        "options": [
            {"id": "a", "text": "The leaf node splits into two nodes, and the median key is copied/pushed up to the parent node", "correct": True},
            {"id": "b", "text": "The entire database is aborted and restarted", "correct": False, "maps_to": "D15", "misconception": "Node splits are standard online maintenance operations"},
            {"id": "c", "text": "The oldest record in the node is deleted", "correct": False, "maps_to": "D17", "misconception": "B+ trees expand dynamically; they never drop records on insert"},
            {"id": "d", "text": "All index pointers are converted into string data", "correct": False, "maps_to": "D17", "misconception": "Nonsensical data conversion"}
        ],
        "explanation": "When a node overflows in a B+ Tree, it splits into two half-full nodes and propagates a key upward to its parent node.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D18: Query Processing & Optimization (12 questions)
    # ==========================================
    {
        "id": "Q_D18_A_01",
        "concept": "D18",
        "family": "A",
        "difficulty": 1,
        "prompt": "What is the primary objective of a Cost-Based Query Optimizer (CBO) in a relational database?",
        "options": [
            {"id": "a", "text": "To evaluate alternative physical execution plans and select the one with the lowest estimated execution cost (I/O, CPU, memory)", "correct": True},
            {"id": "b", "text": "To calculate the financial billing cost of cloud database usage", "correct": False, "maps_to": "D01", "misconception": "Confuses algorithmic query optimization cost with cloud hosting bills"},
            {"id": "c", "text": "To verify user password credentials during login", "correct": False, "maps_to": "D01", "misconception": "Authentication is handled by database access security, not optimizer"},
            {"id": "d", "text": "To rewrite SQL queries in Python syntax", "correct": False, "maps_to": "D01", "misconception": "Optimizer generates physical execution trees, not Python code"}
        ],
        "explanation": "The cost-based optimizer uses table statistics to estimate disk I/O, CPU cycles, and memory usage for different plans, picking the lowest cost plan.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_A_02",
        "concept": "D18",
        "family": "A",
        "difficulty": 2,
        "prompt": "What heuristic optimization rule is commonly known as 'Pushing Down Selections'?",
        "options": [
            {"id": "a", "text": "Applying selection predicates (WHERE filters) as early as possible in the query tree before executing expensive joins and products", "correct": True},
            {"id": "b", "text": "Deferring selection filters until the very end of query execution", "correct": False, "maps_to": "D18", "misconception": "Late filtering carries large intermediate record volumes through joins, wasting CPU and I/O"},
            {"id": "c", "text": "Dropping all WHERE clauses automatically to boost speed", "correct": False, "maps_to": "D08", "misconception": "Altering query semantics violates relational query equivalence"},
            {"id": "d", "text": "Pushing queries from the database server to the client machine", "correct": False, "maps_to": "D01", "misconception": "Confuses relational algebra tree transformations with client/server networking"}
        ],
        "explanation": "Pushing selections down applies filter conditions directly at the scan level, drastically reducing intermediate relation cardinalities before joins occur.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_A_03",
        "concept": "D18",
        "family": "A",
        "difficulty": 2,
        "prompt": "Under what circumstance is a Nested Loop Join typically the most efficient join algorithm?",
        "options": [
            {"id": "a", "text": "When the outer relation is small and the inner relation has an index on the join attribute (Index Nested Loop Join)", "correct": True},
            {"id": "b", "text": "When both tables have 100 million rows and zero indexes", "correct": False, "maps_to": "D18", "misconception": "Nested loop on huge unindexed tables incurs catastrophic O(N*M) complexity"},
            {"id": "c", "text": "When the query uses FULL OUTER JOIN without an ON condition", "correct": False, "maps_to": "D09", "misconception": "Hash or merge joins handle outer joins better"},
            {"id": "d", "text": "When memory is unlimited and tables are pre-sorted", "correct": False, "maps_to": "D18", "misconception": "Pre-sorted tables are best joined using Sort-Merge Join"}
        ],
        "explanation": "If the outer loop has few rows and the inner table has an index on the join key, an index nested loop join performs fast O(1) lookups per outer tuple.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_A_04",
        "concept": "D18",
        "family": "A",
        "difficulty": 3,
        "prompt": "What does a Hash Join algorithm do during its 'Build' phase?",
        "options": [
            {"id": "a", "text": "Reads the smaller relation and constructs an in-memory hash table on the join attribute", "correct": True},
            {"id": "b", "text": "Sorts both tables on disk alphabetically", "correct": False, "maps_to": "D18", "misconception": "Describes the first phase of Sort-Merge Join"},
            {"id": "c", "text": "Generates a B+ Tree index on the table", "correct": False, "maps_to": "D17", "misconception": "Builds a transient hash table, not a permanent B+ Tree"},
            {"id": "d", "text": "Checks for syntax errors in the query statement", "correct": False, "maps_to": "D08", "misconception": "Parsing occurs long before the physical join execution phase"}
        ],
        "explanation": "In Hash Join, the build phase hashes the smaller relation into an in-memory hash table; the subsequent probe phase streams the larger relation through it.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_A_05",
        "concept": "D18",
        "family": "A",
        "difficulty": 1,
        "prompt": "In SQL, what command displays the execution plan chosen by the query optimizer without necessarily executing the query?",
        "options": [
            {"id": "a", "text": "EXPLAIN", "correct": True},
            {"id": "b", "text": "DEBUG", "correct": False, "maps_to": "D18", "misconception": "DEBUG is not standard SQL syntax for execution plans"},
            {"id": "c", "text": "SHOW LOG", "correct": False, "maps_to": "D01", "misconception": "SHOW LOG displays server error logs, not query plans"},
            {"id": "d", "text": "DESCRIBE PLAN", "correct": False, "maps_to": "D18", "misconception": "DESCRIBE checks table schemas; EXPLAIN inspects query execution trees"}
        ],
        "explanation": "EXPLAIN (or EXPLAIN PLAN) displays the chosen query execution path, operators, and estimated costs.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_A_06",
        "concept": "D18",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is Selectivity in query optimization?",
        "options": [
            {"id": "a", "text": "The fraction of tuples in a relation that satisfy a given filter predicate (ranging from 0.0 to 1.0)", "correct": True},
            {"id": "b", "text": "The total number of columns chosen in the SELECT clause", "correct": False, "maps_to": "D08", "misconception": "Confuses selectivity with projection arity"},
            {"id": "c", "text": "The percentage of CPU consumed by the database engine", "correct": False, "maps_to": "D18", "misconception": "Selectivity is a statistical estimate of qualifying rows, not hardware utilization"},
            {"id": "d", "text": "The duration of transaction execution in milliseconds", "correct": False, "maps_to": "D15", "misconception": "Selectivity relates to predicate filtering power"}
        ],
        "explanation": "Selectivity measures how filtering a condition is: highly selective predicates return very few tuples (small fraction), favoring index scans.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_B_01",
        "concept": "D18",
        "family": "B",
        "difficulty": 1,
        "prompt": "Why might a query optimizer choose a Sequential Table Scan over an Index Scan even when an index exists on the filtered column?",
        "options": [
            {"id": "a", "text": "The query has low selectivity (it retrieves a large portion of the table, e.g. 80%), making sequential bulk I/O faster than scattered random index lookups", "correct": True},
            {"id": "b", "text": "The database optimizer is broken and cannot detect indexes", "correct": False, "maps_to": "D18", "misconception": "Cost-based optimizers intentionally favor sequential scans when scattered random I/O is slower"},
            {"id": "c", "text": "Sequential scans are always faster than index scans regardless of table size", "correct": False, "maps_to": "D18", "misconception": "Index scans are drastically faster for point lookups and small ranges"},
            {"id": "d", "text": "Index scans are forbidden on weekdays", "correct": False, "maps_to": "D01", "misconception": "Absurd scheduling myth"}
        ],
        "explanation": "Sequential scans read continuous disk blocks at high throughput. When retrieving a high fraction of rows, scattered random I/O from an index is slower.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_B_02",
        "concept": "D18",
        "family": "B",
        "difficulty": 2,
        "prompt": "How does Sort-Merge Join operate when joining two relations R and S on an equality attribute?",
        "options": [
            {"id": "a", "text": "Both relations are sorted on the join key (if not already sorted), and then scanned concurrently in lockstep to match identical keys", "correct": True},
            {"id": "b", "text": "A hash function partitions rows into random buckets", "correct": False, "maps_to": "D18", "misconception": "Describes Hash Join, not Sort-Merge Join"},
            {"id": "c", "text": "Every row in R is paired with every row in S sequentially", "correct": False, "maps_to": "D07", "misconception": "Describes Cartesian product / nested loop join"},
            {"id": "d", "text": "The tables are merged permanently into a single file on disk", "correct": False, "maps_to": "D01", "misconception": "Sort-Merge Join is a query execution operator, not permanent disk restructuring"}
        ],
        "explanation": "Sort-Merge Join sorts both inputs by the join key and merges them in linear time O(N + M). Highly efficient if inputs are already sorted by clustered indexes.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_B_03",
        "concept": "D18",
        "family": "B",
        "difficulty": 2,
        "prompt": "What is the difference between EXPLAIN and EXPLAIN ANALYZE in database management systems like PostgreSQL?",
        "options": [
            {"id": "a", "text": "EXPLAIN produces estimated costs based on optimizer statistics without running the query, while EXPLAIN ANALYZE actually executes the query and shows real runtime metrics", "correct": True},
            {"id": "b", "text": "EXPLAIN ANALYZE runs only on views, while EXPLAIN runs on base tables", "correct": False, "maps_to": "D11", "misconception": "Both commands apply to any valid SQL query"},
            {"id": "c", "text": "EXPLAIN deletes slow indexes automatically", "correct": False, "maps_to": "D17", "misconception": "Neither command alters schema indexes"},
            {"id": "d", "text": "There is no difference; they produce identical text output", "correct": False, "maps_to": "D18", "misconception": "EXPLAIN ANALYZE includes actual execution time, actual rows, and buffer hits"}
        ],
        "explanation": "EXPLAIN shows purely theoretical cost estimates. EXPLAIN ANALYZE actually executes the query to report real elapsed times and row counts.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_B_04",
        "concept": "D18",
        "family": "B",
        "difficulty": 3,
        "prompt": "Why are accurate, up-to-date database statistics (e.g. histograms, distinct value counts) vital for the query optimizer?",
        "options": [
            {"id": "a", "text": "Stale statistics cause the optimizer to miscalculate selectivity, potentially choosing disastrous plans like nested loop joins over millions of rows", "correct": True},
            {"id": "b", "text": "Outdated statistics cause the database to reject all incoming client connections", "correct": False, "maps_to": "D01", "misconception": "Stale statistics affect query planning quality, not network connection handshakes"},
            {"id": "c", "text": "Statistics are required to decrypt passwords", "correct": False, "maps_to": "D01", "misconception": "Confuses optimizer statistics with cryptographic salts"},
            {"id": "d", "text": "Statistics prevent tables from reaching maximum row limits", "correct": False, "maps_to": "D02", "misconception": "Statistics have no role in storage capacity limits"}
        ],
        "explanation": "The cost-based optimizer relies entirely on catalog statistics to estimate intermediate cardinalities; inaccurate statistics lead to bad execution plans.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_B_05",
        "concept": "D18",
        "family": "B",
        "difficulty": 1,
        "prompt": "What is Cardinality Estimation in query optimization?",
        "options": [
            {"id": "a", "text": "Estimating the number of rows that will be produced by each operator in the execution plan tree", "correct": True},
            {"id": "b", "text": "Counting the number of letters in column names", "correct": False, "maps_to": "D08", "misconception": "Trivial string length misunderstanding"},
            {"id": "c", "text": "Measuring network ping latency between database and client", "correct": False, "maps_to": "D01", "misconception": "Confuses database cardinalities with network ping times"},
            {"id": "d", "text": "Calculating the total disk capacity of the server", "correct": False, "maps_to": "D01", "misconception": "Cardinality estimation predicts intermediate query row counts"}
        ],
        "explanation": "Cardinality estimation predicts how many rows will output from table scans, filters, and joins, forming the basis for operator cost calculations.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D18_B_06",
        "concept": "D18",
        "family": "B",
        "difficulty": 2,
        "prompt": "In relational algebra optimization, what does 'Projection Pushdown' achieve?",
        "options": [
            {"id": "a", "text": "Eliminates unneeded columns as early as possible to minimize memory footprint and tuple width during intermediate joins", "correct": True},
            {"id": "b", "text": "Removes WHERE clauses to speed up sorting", "correct": False, "maps_to": "D08", "misconception": "Projections eliminate columns (attributes), not filter predicates"},
            {"id": "c", "text": "Forces the database to display results using projector screens", "correct": False, "maps_to": "D01", "misconception": "Humorous confusion with display hardware"},
            {"id": "d", "text": "Converts all numbers into floating-point decimals", "correct": False, "maps_to": "D02", "misconception": "Projection has nothing to do with numeric type casting"}
        ],
        "explanation": "Projection pushdown discards unreferenced attributes as soon as possible, shrinking intermediate tuple sizes and conserving memory buffers.",
        "validation_status": "reviewed"
    }
]
