"""
Part 1 of 200 Question Bank:
Concepts D01, D02, D03, D04, D05, D06 (66 questions total, 11 per concept)
"""

QUESTIONS_PART1 = [
    # ==========================================
    # D01: DBMS Basics (11 questions)
    # ==========================================
    {
        "id": "Q_D01_A_01",
        "concept": "D01",
        "family": "A",
        "difficulty": 1,
        "prompt": "Which component of the DBMS environment stores metadata, including table definitions, constraints, and index descriptions?",
        "options": [
            {"id": "a", "text": "Operating System File Allocation Table", "correct": False, "maps_to": "D01", "misconception": "Assumes database catalog metadata is managed directly by OS file systems"},
            {"id": "b", "text": "Data Dictionary / System Catalog", "correct": True},
            {"id": "c", "text": "Query Execution Buffer Cache", "correct": False, "maps_to": "D18", "misconception": "Confuses transient memory buffers with persistent schema catalogs"},
            {"id": "d", "text": "Transaction Write-Ahead Log", "correct": False, "maps_to": "D15", "misconception": "Confuses recovery redo logs with schema metadata catalogs"}
        ],
        "explanation": "The Data Dictionary (or System Catalog) holds metadata (data about data), such as relation schemas, constraints, privileges, and storage details.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_A_02",
        "concept": "D01",
        "family": "A",
        "difficulty": 2,
        "prompt": "A developer modifies an existing table by adding a new attribute 'middle_name' and creating a view that hides it for legacy users. Which concept ensures existing applications remain unaffected?",
        "options": [
            {"id": "a", "text": "Physical Data Independence", "correct": False, "maps_to": "D01", "misconception": "Confuses physical disk layout independence with logical schema insulation"},
            {"id": "b", "text": "Logical Data Independence", "correct": True},
            {"id": "c", "text": "Atomicity Guarantee", "correct": False, "maps_to": "D15", "misconception": "Confuses schema evolution independence with transaction atomicity"},
            {"id": "d", "text": "Referential Integrity", "correct": False, "maps_to": "D04", "misconception": "Confuses foreign key constraints with view abstraction layers"}
        ],
        "explanation": "Logical Data Independence allows the conceptual schema to be altered without altering existing external schemas or applications.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_A_03",
        "concept": "D01",
        "family": "A",
        "difficulty": 2,
        "prompt": "Why does a traditional file processing system struggle with concurrent multi-user writes compared to a DBMS?",
        "options": [
            {"id": "a", "text": "File systems lack coordinated locking protocols and crash-safe transaction logging", "correct": True},
            {"id": "b", "text": "Operating systems cannot store records exceeding 1 kilobyte", "correct": False, "maps_to": "D01", "misconception": "Incorrectly attributes concurrency failure to arbitrary file size limits"},
            {"id": "c", "text": "File systems enforce strict serializability that rejects all parallel reads", "correct": False, "maps_to": "D16", "misconception": "Assumes file systems provide stricter database serializability than DBMS"},
            {"id": "d", "text": "File systems store data solely in volatile RAM memory", "correct": False, "maps_to": "D01", "misconception": "Confuses persistent disk storage with in-memory volatile structures"}
        ],
        "explanation": "File processing systems lack coordinated concurrency control (like granular row-level locking) and ACID recovery protocols.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_A_04",
        "concept": "D01",
        "family": "A",
        "difficulty": 1,
        "prompt": "In the ANSI-SPARC three-tier architecture, what level describes how users and applications perceive the database data?",
        "options": [
            {"id": "a", "text": "Internal Level", "correct": False, "maps_to": "D01", "misconception": "Confuses physical storage structures with end-user views"},
            {"id": "b", "text": "Conceptual Level", "correct": False, "maps_to": "D01", "misconception": "Confuses overall enterprise logical model with individualized user views"},
            {"id": "c", "text": "External (View) Level", "correct": True},
            {"id": "d", "text": "Physical Storage Engine Level", "correct": False, "maps_to": "D01", "misconception": "Confuses storage subsystem with the external application view"}
        ],
        "explanation": "The External Level consists of multiple external schemas or user views, tailored specifically to individual user groups.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_A_05",
        "concept": "D01",
        "family": "A",
        "difficulty": 3,
        "prompt": "Which of the following database alterations is an example of exercising Physical Data Independence?",
        "options": [
            {"id": "a", "text": "Partitioning an existing table vertically into two separate normalized tables", "correct": False, "maps_to": "D13", "misconception": "Table decomposition changes the logical/conceptual schema, not physical storage"},
            {"id": "b", "text": "Switching the primary index from a B+ Tree to a Hash Index without altering SQL query statements", "correct": True},
            {"id": "c", "text": "Renaming a table column and creating a synonym alias", "correct": False, "maps_to": "D01", "misconception": "Column renaming is a conceptual schema transformation"},
            {"id": "d", "text": "Adding a foreign key constraint between orders and customers", "correct": False, "maps_to": "D04", "misconception": "Constraint definitions belong to the conceptual/logical layer"}
        ],
        "explanation": "Physical Data Independence is the ability to change the internal schema (e.g. index structures or storage organization) without changing the conceptual schema.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_A_06",
        "concept": "D01",
        "family": "A",
        "difficulty": 2,
        "prompt": "What role does the Conceptual Schema serve in the three-level database architecture?",
        "options": [
            {"id": "a", "text": "It provides a global community view of the entire database structure, hiding physical storage details", "correct": True},
            {"id": "b", "text": "It defines disk block allocation, cylinder groupings, and page offsets", "correct": False, "maps_to": "D01", "misconception": "Assigns internal physical storage definitions to conceptual schema"},
            {"id": "c", "text": "It is restricted strictly to user interface HTML form representations", "correct": False, "maps_to": "D01", "misconception": "Confuses database conceptual models with client presentation tiers"},
            {"id": "d", "text": "It stores transaction undo/redo logs during server recovery", "correct": False, "maps_to": "D15", "misconception": "Confuses transaction logs with schema architecture tiers"}
        ],
        "explanation": "The Conceptual Schema represents the logical structure of the entire database for all users, including entities, relationships, and constraints.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_B_01",
        "concept": "D01",
        "family": "B",
        "difficulty": 1,
        "prompt": "A DBA rebuilds table indexes and reorganizes data files onto a fast NVMe storage pool. User queries continue without modification. What principle is demonstrated?",
        "options": [
            {"id": "a", "text": "Logical Data Independence", "correct": False, "maps_to": "D01", "misconception": "Mistakes physical file rearrangement for conceptual schema changes"},
            {"id": "b", "text": "Physical Data Independence", "correct": True},
            {"id": "c", "text": "Functional Dependency Normalization", "correct": False, "maps_to": "D12", "misconception": "Confuses hardware storage layout with relational functional dependency"},
            {"id": "d", "text": "Isolation Serialization", "correct": False, "maps_to": "D16", "misconception": "Confuses disk migration with transaction concurrency levels"}
        ],
        "explanation": "Physical Data Independence ensures modifications to internal storage structures require no changes to conceptual schemas or queries.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_B_02",
        "concept": "D01",
        "family": "B",
        "difficulty": 2,
        "prompt": "A company splits an 'Employees' table into two tables, but provides an updatable view named 'Employees' for existing client apps. Which principle enables this?",
        "options": [
            {"id": "a", "text": "Logical Data Independence", "correct": True},
            {"id": "b", "text": "Physical Data Independence", "correct": False, "maps_to": "D01", "misconception": "Confuses logical table splitting with storage device independence"},
            {"id": "c", "text": "Strict 2-Phase Locking", "correct": False, "maps_to": "D16", "misconception": "Confuses schema restructuring with concurrency locking protocols"},
            {"id": "d", "text": "Domain Value Atomicity", "correct": False, "maps_to": "D02", "misconception": "Confuses view restructuring with atomic scalar domains"}
        ],
        "explanation": "Providing views that map to altered conceptual relations preserves Logical Data Independence for external client programs.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_B_03",
        "concept": "D01",
        "family": "B",
        "difficulty": 1,
        "prompt": "Which of the following is considered a primary risk of storing enterprise operational data in standalone flat files rather than a DBMS?",
        "options": [
            {"id": "a", "text": "Data redundancy and uncontrolled update anomalies across programs", "correct": True},
            {"id": "b", "text": "Complete inability to store numeric data types", "correct": False, "maps_to": "D01", "misconception": "Believes flat files cannot hold numeric data strings"},
            {"id": "c", "text": "Compulsory enforcement of BCNF schema normalizations", "correct": False, "maps_to": "D14", "misconception": "Attributes advanced relational normalization rules to plain flat files"},
            {"id": "d", "text": "Mandatory requirement of distributed two-phase commit", "correct": False, "maps_to": "D15", "misconception": "Confuses distributed database consensus with flat file storage"}
        ],
        "explanation": "Flat files lack centralized constraint validation and declarative schemas, routinely causing duplicate data and anomalies.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_B_04",
        "concept": "D01",
        "family": "B",
        "difficulty": 2,
        "prompt": "Which mapping in the three-schema architecture translates a user's query against a view into operations on conceptual relations?",
        "options": [
            {"id": "a", "text": "External/Conceptual Mapping", "correct": True},
            {"id": "b", "text": "Conceptual/Internal Mapping", "correct": False, "maps_to": "D01", "misconception": "Confuses external view mapping with conceptual-to-disk block mapping"},
            {"id": "c", "text": "Operating System VFS Layer", "correct": False, "maps_to": "D01", "misconception": "Places SQL view resolution inside OS filesystem drivers"},
            {"id": "d", "text": "Network Socket Serialization Layer", "correct": False, "maps_to": "D01", "misconception": "Confuses network transport with relational schema mappings"}
        ],
        "explanation": "External/Conceptual mapping bridges external view definitions with the underlying conceptual tables.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_B_05",
        "concept": "D01",
        "family": "B",
        "difficulty": 3,
        "prompt": "When a DBMS processes a Data Definition Language (DDL) command such as CREATE TABLE, what primary action occurs?",
        "options": [
            {"id": "a", "text": "The DBMS parses the definition and updates the system catalog tables with new metadata", "correct": True},
            {"id": "b", "text": "The DBMS writes all future data rows directly to volatile cache memory", "correct": False, "maps_to": "D01", "misconception": "Believes DDL command pre-allocates unwritten data rows into RAM"},
            {"id": "c", "text": "The DBMS executes an immediate full-database checkpoint and halts", "correct": False, "maps_to": "D15", "misconception": "Confuses schema registration with complete system checkpoint freezing"},
            {"id": "d", "text": "The DBMS replaces all client application binary executables", "correct": False, "maps_to": "D01", "misconception": "Confuses server-side schema catalog update with client binary recompilation"}
        ],
        "explanation": "DDL commands are compiled and recorded into the Data Dictionary/System Catalog, establishing schemas and descriptors.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D02: Relational Model (11 questions)
    # ==========================================
    {
        "id": "Q_D02_A_01",
        "concept": "D02",
        "family": "A",
        "difficulty": 1,
        "prompt": "In the formal relational model, what is the mathematical term for a row in a relation?",
        "options": [
            {"id": "a", "text": "Tuple", "correct": True},
            {"id": "b", "text": "Domain", "correct": False, "maps_to": "D02", "misconception": "Confuses the set of permitted scalar values (domain) with a record row"},
            {"id": "c", "text": "Attribute", "correct": False, "maps_to": "D02", "misconception": "Confuses table column (attribute) with record row"},
            {"id": "d", "text": "Cardinality", "correct": False, "maps_to": "D02", "misconception": "Confuses count of tuples with a single tuple item"}
        ],
        "explanation": "A row in a relational table corresponds mathematically to an ordered list of attribute values called a tuple.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_A_02",
        "concept": "D02",
        "family": "A",
        "difficulty": 2,
        "prompt": "If a relation R has 4 attributes and currently holds 100 tuples, what are its degree and cardinality respectively?",
        "options": [
            {"id": "a", "text": "Degree = 4, Cardinality = 100", "correct": True},
            {"id": "b", "text": "Degree = 100, Cardinality = 4", "correct": False, "maps_to": "D02", "misconception": "Inverts the definitions of degree (column count) and cardinality (row count)"},
            {"id": "c", "text": "Degree = 400, Cardinality = 100", "correct": False, "maps_to": "D02", "misconception": "Multiplies attributes by tuples instead of taking column count for degree"},
            {"id": "d", "text": "Degree = 4, Cardinality = 400", "correct": False, "maps_to": "D02", "misconception": "Multiplies attributes by tuples for cardinality instead of counting rows"}
        ],
        "explanation": "The degree of a relation is the number of attributes (4), and cardinality is the number of tuples (100).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_A_03",
        "concept": "D02",
        "family": "A",
        "difficulty": 2,
        "prompt": "According to relational model theory, why can a mathematical relation never contain duplicate tuples?",
        "options": [
            {"id": "a", "text": "A relation is formally defined as a mathematical set of tuples, and sets do not contain duplicate elements", "correct": True},
            {"id": "b", "text": "Hardware storage controllers reject duplicate byte writes automatically", "correct": False, "maps_to": "D01", "misconception": "Attributes formal set-theoretic uniqueness to hardware disk drivers"},
            {"id": "c", "text": "SQL engines convert all tables into linked lists", "correct": False, "maps_to": "D02", "misconception": "Confuses relational theory with memory data structures"},
            {"id": "d", "text": "Duplicate tuples would cause infinite loops during disk reads", "correct": False, "maps_to": "D02", "misconception": "Imagines disk I/O loops rather than recognizing set uniqueness"}
        ],
        "explanation": "A relation instance is mathematically defined as a set of tuples, and mathematical sets cannot contain duplicate elements.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_A_04",
        "concept": "D02",
        "family": "A",
        "difficulty": 1,
        "prompt": "What does attribute domain refer to in relational databases?",
        "options": [
            {"id": "a", "text": "The physical directory path where the database tablespace is mounted", "correct": False, "maps_to": "D01", "misconception": "Confuses OS directory paths with relational attribute domain definitions"},
            {"id": "b", "text": "The set of all permissible atomic values that can be assigned to an attribute", "correct": True},
            {"id": "c", "text": "The total number of rows present in the relation", "correct": False, "maps_to": "D02", "misconception": "Confuses domain definition with cardinality"},
            {"id": "d", "text": "The network domain controller governing user logins", "correct": False, "maps_to": "D01", "misconception": "Confuses LDAP/Windows domain with database relational attribute domain"}
        ],
        "explanation": "A domain is the set of permissible atomic scalar values valid for an attribute.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_A_05",
        "concept": "D02",
        "family": "A",
        "difficulty": 3,
        "prompt": "In three-valued logic (3VL) adopted by relational systems for NULL handling, what is the boolean outcome of: (TRUE OR NULL) AND (NOT NULL)?",
        "options": [
            {"id": "a", "text": "TRUE", "correct": False, "maps_to": "D02", "misconception": "Treats (NOT NULL) as TRUE instead of UNKNOWN"},
            {"id": "b", "text": "FALSE", "correct": False, "maps_to": "D02", "misconception": "Incorrectly evaluates 3VL boolean operations to FALSE"},
            {"id": "c", "text": "UNKNOWN (NULL)", "correct": True},
            {"id": "d", "text": "Syntax Error", "correct": False, "maps_to": "D08", "misconception": "Believes three-valued boolean logic yields a syntax error in relational theory"}
        ],
        "explanation": "TRUE OR NULL is TRUE. NOT NULL is UNKNOWN. TRUE AND UNKNOWN is UNKNOWN.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_A_06",
        "concept": "D02",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is the key distinction between a relation schema R and a relation state r(R)?",
        "options": [
            {"id": "a", "text": "The schema is the static structural definition, whereas the state is the dynamic set of tuples at a specific point in time", "correct": True},
            {"id": "b", "text": "The schema contains data rows, whereas the state contains index pointers", "correct": False, "maps_to": "D02", "misconception": "Reverses the concepts of schema definitions and instance rows"},
            {"id": "c", "text": "The schema is stored in cache, while the state is stored in configuration files", "correct": False, "maps_to": "D01", "misconception": "Confuses architectural definitions with memory caching locations"},
            {"id": "d", "text": "A relation state never changes after table creation", "correct": False, "maps_to": "D02", "misconception": "Believes relation state is immutable rather than dynamic"}
        ],
        "explanation": "Relation schema is the static structure/type specification; relation state represents the current collection of tuples.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_B_01",
        "concept": "D02",
        "family": "B",
        "difficulty": 1,
        "prompt": "If relation Students(StudentID, Name, Major, GPA) has degree 4, and 30 new students are enrolled, what is the new degree of the relation?",
        "options": [
            {"id": "a", "text": "34", "correct": False, "maps_to": "D02", "misconception": "Adds tuples to attributes when calculating degree"},
            {"id": "b", "text": "4", "correct": True},
            {"id": "c", "text": "120", "correct": False, "maps_to": "D02", "misconception": "Multiplies degree by tuple increments"},
            {"id": "d", "text": "30", "correct": False, "maps_to": "D02", "misconception": "Confuses degree with cardinality"}
        ],
        "explanation": "Adding rows changes the cardinality of the relation, but the degree (number of attributes) remains 4.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_B_02",
        "concept": "D02",
        "family": "B",
        "difficulty": 2,
        "prompt": "Why is the order of tuples within a relational table considered irrelevant in formal relational theory?",
        "options": [
            {"id": "a", "text": "Because relations are mathematical sets, and sets have no inherent ordering of their elements", "correct": True},
            {"id": "b", "text": "Because relational storage systems randomize records to prevent disk wear", "correct": False, "maps_to": "D01", "misconception": "Confuses mathematical set properties with hardware disk wear leveling"},
            {"id": "c", "text": "Because SQL requires all queries to specify ORDER BY anyway", "correct": False, "maps_to": "D08", "misconception": "Believes ordering is ignored simply due to SQL syntax options"},
            {"id": "d", "text": "Because relational engines only support FIFO queues", "correct": False, "maps_to": "D02", "misconception": "Misidentifies relational storage as a FIFO queue structure"}
        ],
        "explanation": "Relations are defined as unordered mathematical sets of tuples. Physical ordering is an implementation artifact.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_B_03",
        "concept": "D02",
        "family": "B",
        "difficulty": 2,
        "prompt": "What does the atomic value rule require under the classical relational model?",
        "options": [
            {"id": "a", "text": "Each attribute value in a tuple must be an indivisible scalar value, not a list, set, or nested record", "correct": True},
            {"id": "b", "text": "Every update transaction must complete in exactly one nanosecond", "correct": False, "maps_to": "D15", "misconception": "Confuses attribute domain atomicity with transaction execution speed"},
            {"id": "c", "text": "All columns must use 64-bit integer values only", "correct": False, "maps_to": "D02", "misconception": "Restricts atomic types arbitrarily to 64-bit integers"},
            {"id": "d", "text": "A table can contain at most one column per primary key", "correct": False, "maps_to": "D03", "misconception": "Confuses scalar value atomicity with composite key structures"}
        ],
        "explanation": "First Normal Form and relational foundation require that attribute domains consist of atomic (indivisible) scalar values.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_B_04",
        "concept": "D02",
        "family": "B",
        "difficulty": 3,
        "prompt": "In three-valued logic (3VL), what is the evaluation of the expression: NULL = NULL?",
        "options": [
            {"id": "a", "text": "TRUE", "correct": False, "maps_to": "D02", "misconception": "Assumes two unknown values are equal to each other"},
            {"id": "b", "text": "FALSE", "correct": False, "maps_to": "D02", "misconception": "Assumes equality of unknowns evaluates to boolean FALSE"},
            {"id": "c", "text": "UNKNOWN (NULL)", "correct": True},
            {"id": "d", "text": "UNDEFINED", "correct": False, "maps_to": "D08", "misconception": "Confuses 3VL UNKNOWN with programming language runtime undefined state"}
        ],
        "explanation": "NULL signifies missing/unknown data. Two unknown values cannot be asserted as equal, yielding UNKNOWN.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D02_B_05",
        "concept": "D02",
        "family": "B",
        "difficulty": 1,
        "prompt": "What distinguishes SQL tables from pure relational model relations regarding duplicate rows?",
        "options": [
            {"id": "a", "text": "SQL tables are multisets (bags) by default and permit duplicate rows unless a constraint is defined", "correct": True},
            {"id": "b", "text": "Pure relations allow duplicate rows while SQL completely forbids them without exceptions", "correct": False, "maps_to": "D02", "misconception": "Reverses the multiset vs set behavior of SQL and relational theory"},
            {"id": "c", "text": "Neither SQL nor the relational model allows duplicate rows under any circumstances", "correct": False, "maps_to": "D02", "misconception": "Overlooks that SQL tables are bags (multisets) unless constrained by primary/unique keys"},
            {"id": "d", "text": "SQL tables can only hold rows if all columns are character strings", "correct": False, "maps_to": "D08", "misconception": "Fabricates a constraint restricting SQL tables to string data"}
        ],
        "explanation": "SQL tables are multisets (bags) allowing duplicate rows unless restricted by PRIMARY KEY or UNIQUE constraints.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D03: Keys (11 questions)
    # ==========================================
    {
        "id": "Q_D03_A_01",
        "concept": "D03",
        "family": "A",
        "difficulty": 1,
        "prompt": "What defines a candidate key in a relational schema?",
        "options": [
            {"id": "a", "text": "Any attribute that contains non-null numeric values", "correct": False, "maps_to": "D03", "misconception": "Confuses data type characteristics with uniqueness constraints"},
            {"id": "b", "text": "A minimal superkey—a set of attributes with uniqueness where no proper subset is unique", "correct": True},
            {"id": "c", "text": "A foreign key that references a weak entity", "correct": False, "maps_to": "D04", "misconception": "Confuses foreign key references with candidate keys"},
            {"id": "d", "text": "All attributes in the table combined together", "correct": False, "maps_to": "D03", "misconception": "Confuses trivial superkeys with minimal candidate keys"}
        ],
        "explanation": "A candidate key is a minimal superkey: it possesses uniqueness, and no proper subset has uniqueness.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_A_02",
        "concept": "D03",
        "family": "A",
        "difficulty": 2,
        "prompt": "Given relation R(A, B, C, D) where {A, B} is a candidate key. Which of the following sets is guaranteed to be a superkey?",
        "options": [
            {"id": "a", "text": "{A}", "correct": False, "maps_to": "D03", "misconception": "Believes a subset of a candidate key retains uniqueness"},
            {"id": "b", "text": "{B, C}", "correct": False, "maps_to": "D03", "misconception": "Assumes combining non-key attributes produces a key"},
            {"id": "c", "text": "{A, B, C}", "correct": True},
            {"id": "d", "text": "{C, D}", "correct": False, "maps_to": "D03", "misconception": "Ignores candidate key attributes when evaluating superkeys"}
        ],
        "explanation": "A superkey is any superset of a candidate key. Any set containing both A and B is guaranteed to be a superkey.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_A_03",
        "concept": "D03",
        "family": "A",
        "difficulty": 2,
        "prompt": "In relation R(SSN, Email, StudentID, FullName), both SSN and Email are candidate keys. If SSN is chosen as Primary Key, what is Email called?",
        "options": [
            {"id": "a", "text": "Foreign Key", "correct": False, "maps_to": "D04", "misconception": "Confuses alternative candidate keys with referential foreign keys"},
            {"id": "b", "text": "Alternate Key", "correct": True},
            {"id": "c", "text": "Composite Key", "correct": False, "maps_to": "D03", "misconception": "Single-attribute keys are not composite keys"},
            {"id": "d", "text": "Surrogate Key", "correct": False, "maps_to": "D03", "misconception": "Email is a natural key, not a system-generated surrogate key"}
        ],
        "explanation": "Candidate keys that are not selected as the primary key are designated as alternate keys.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_A_04",
        "concept": "D03",
        "family": "A",
        "difficulty": 3,
        "prompt": "Can a foreign key attribute in a child table contain NULL values?",
        "options": [
            {"id": "a", "text": "No, foreign keys must always be non-null under entity integrity", "correct": False, "maps_to": "D04", "misconception": "Confuses primary key NOT NULL rule with foreign key rules"},
            {"id": "b", "text": "Yes, unless explicitly restricted by a NOT NULL constraint, indicating optional relationship participation", "correct": True},
            {"id": "c", "text": "Only if the parent table has a row whose primary key value is NULL", "correct": False, "maps_to": "D04", "misconception": "Primary keys can never contain NULL values"},
            {"id": "d", "text": "Foreign keys can only contain NULL if the table has zero rows", "correct": False, "maps_to": "D03", "misconception": "Fabricates row count restrictions on NULL foreign key values"}
        ],
        "explanation": "Referential integrity permits foreign keys to be NULL (indicating optional participation) unless restricted by NOT NULL.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_A_05",
        "concept": "D03",
        "family": "A",
        "difficulty": 1,
        "prompt": "What is a surrogate key?",
        "options": [
            {"id": "a", "text": "A natural attribute that carries inherent real-world business meaning, such as National Tax ID", "correct": False, "maps_to": "D03", "misconception": "Confuses natural keys with artificial surrogate keys"},
            {"id": "b", "text": "An artificial, system-assigned unique identifier (e.g. auto-incrementing integer or UUID) with no business meaning", "correct": True},
            {"id": "c", "text": "A key formed by concatenating all foreign keys in a database", "correct": False, "maps_to": "D06", "misconception": "Confuses composite junction keys with single surrogate keys"},
            {"id": "d", "text": "A key used solely for encrypting database backups", "correct": False, "maps_to": "D01", "misconception": "Confuses cryptographic security keys with relational database surrogate keys"}
        ],
        "explanation": "A surrogate key is an artificial unique identifier generated by the DBMS that has no business significance.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_A_06",
        "concept": "D03",
        "family": "A",
        "difficulty": 2,
        "prompt": "What characterizes a composite primary key?",
        "options": [
            {"id": "a", "text": "It consists of two or more attributes combined to form the primary key", "correct": True},
            {"id": "b", "text": "It references primary keys across two different databases simultaneously", "correct": False, "maps_to": "D03", "misconception": "Confuses multi-attribute keys with distributed database federation"},
            {"id": "c", "text": "It permits duplicate values across all constituent columns simultaneously", "correct": False, "maps_to": "D03", "misconception": "Primary keys by definition forbid duplicate combination values"},
            {"id": "d", "text": "It requires all columns in the table to be included in the key", "correct": False, "maps_to": "D03", "misconception": "Confuses composite key with all-attribute relation key"}
        ],
        "explanation": "A composite key is composed of two or more attributes to uniquely identify a record.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_B_01",
        "concept": "D03",
        "family": "B",
        "difficulty": 1,
        "prompt": "Which statement correctly describes the relationship between superkeys and candidate keys?",
        "options": [
            {"id": "a", "text": "Every superkey is a candidate key", "correct": False, "maps_to": "D03", "misconception": "Assumes non-minimal superkeys are candidate keys"},
            {"id": "b", "text": "Every candidate key is a superkey", "correct": True},
            {"id": "c", "text": "A candidate key must have strictly more attributes than any superkey", "correct": False, "maps_to": "D03", "misconception": "Inverts attribute count relationship between candidate keys and superkeys"},
            {"id": "d", "text": "Superkeys never enforce uniqueness across tuples", "correct": False, "maps_to": "D03", "misconception": "Superkeys by definition enforce tuple uniqueness"}
        ],
        "explanation": "All candidate keys satisfy uniqueness and are therefore superkeys. Superkeys with extraneous attributes are not candidate keys.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_B_02",
        "concept": "D03",
        "family": "B",
        "difficulty": 2,
        "prompt": "If relation Enrollments(StudentID, CourseID, Semester, Grade) uses {StudentID, CourseID, Semester} as primary key, what is true about Grade?",
        "options": [
            {"id": "a", "text": "Grade is a non-prime attribute", "correct": True},
            {"id": "b", "text": "Grade is a candidate key on its own", "correct": False, "maps_to": "D03", "misconception": "Mistakes dependent non-prime attribute for candidate key"},
            {"id": "c", "text": "Grade cannot be NULL even if unassigned", "correct": False, "maps_to": "D04", "misconception": "Non-prime attributes can be NULL unless constrained by NOT NULL"},
            {"id": "d", "text": "Grade is part of the composite primary key", "correct": False, "maps_to": "D03", "misconception": "Incorrectly includes non-key column into the stated primary key"}
        ],
        "explanation": "An attribute that is not part of any candidate key is a non-prime attribute.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_B_03",
        "concept": "D03",
        "family": "B",
        "difficulty": 2,
        "prompt": "Why is choosing a frequently updated natural attribute (such as Employee Phone Number) as a primary key generally considered poor design?",
        "options": [
            {"id": "a", "text": "Cascading updates across child foreign keys degrade performance and risk integrity errors", "correct": True},
            {"id": "b", "text": "SQL standards strictly forbid foreign keys referencing phone numbers", "correct": False, "maps_to": "D08", "misconception": "Believes SQL forbids specific string domains as foreign keys"},
            {"id": "c", "text": "Phone numbers cannot be indexed with B+ Trees", "correct": False, "maps_to": "D17", "misconception": "B+ Trees can index any comparable data type"},
            {"id": "d", "text": "Primary keys must always be single-digit numbers", "correct": False, "maps_to": "D03", "misconception": "Fabricates an invalid single-digit restriction on primary keys"}
        ],
        "explanation": "Primary keys should be immutable; updating a primary key requires cascading updates to all referencing foreign key rows.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_B_04",
        "concept": "D03",
        "family": "B",
        "difficulty": 3,
        "prompt": "Can a foreign key reference an attribute in the parent table that is marked UNIQUE but is NOT the primary key?",
        "options": [
            {"id": "a", "text": "Yes, standard SQL allows foreign keys to reference any candidate key or unique constraint", "correct": True},
            {"id": "b", "text": "No, foreign keys can only reference the primary key column", "correct": False, "maps_to": "D03", "misconception": "Believes referential integrity is strictly restricted to primary key columns"},
            {"id": "c", "text": "Only if the parent table has no primary key defined", "correct": False, "maps_to": "D04", "misconception": "Thinks referencing UNIQUE columns is a fallback when PK is absent"},
            {"id": "d", "text": "Only if both tables share the same table owner", "correct": False, "maps_to": "D01", "misconception": "Confuses database permissions with relational integrity rules"}
        ],
        "explanation": "A foreign key may reference any column set with a UNIQUE constraint in the referenced table.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_B_05",
        "concept": "D03",
        "family": "B",
        "difficulty": 1,
        "prompt": "In an Orders table, OrderID is the primary key and CustomerID references the Customers table. What is CustomerID in the Orders table?",
        "options": [
            {"id": "a", "text": "Foreign Key", "correct": True},
            {"id": "b", "text": "Alternate Key", "correct": False, "maps_to": "D03", "misconception": "Confuses foreign key with alternate candidate key"},
            {"id": "c", "text": "Surrogate Key", "correct": False, "maps_to": "D03", "misconception": "CustomerID in Orders is a foreign key, not the surrogate key of Orders"},
            {"id": "d", "text": "Superkey", "correct": False, "maps_to": "D03", "misconception": "A customer can place multiple orders, so CustomerID does not uniquely identify Orders"}
        ],
        "explanation": "CustomerID in Orders references the primary key of Customers, making it a foreign key.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D04: Integrity Constraints (11 questions)
    # ==========================================
    {
        "id": "Q_D04_A_01",
        "concept": "D04",
        "family": "A",
        "difficulty": 1,
        "prompt": "Which integrity rule states that no primary key value may be NULL?",
        "options": [
            {"id": "a", "text": "Entity Integrity", "correct": True},
            {"id": "b", "text": "Referential Integrity", "correct": False, "maps_to": "D04", "misconception": "Confuses entity integrity (PK NOT NULL) with referential integrity (FK validity)"},
            {"id": "c", "text": "Domain Integrity", "correct": False, "maps_to": "D04", "misconception": "Confuses domain data type rules with primary key non-null enforcement"},
            {"id": "d", "text": "Serializability Integrity", "correct": False, "maps_to": "D16", "misconception": "Confuses transaction scheduling with static table integrity"}
        ],
        "explanation": "Entity Integrity states that no primary key attribute of a base relation may be NULL.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_A_02",
        "concept": "D04",
        "family": "A",
        "difficulty": 2,
        "prompt": "If a foreign key is created with ON DELETE CASCADE, what happens when a referenced record in the parent table is deleted?",
        "options": [
            {"id": "a", "text": "All matching referencing rows in the child table are automatically deleted", "correct": True},
            {"id": "b", "text": "The deletion in the parent table is aborted with an integrity violation error", "correct": False, "maps_to": "D04", "misconception": "Describes ON DELETE RESTRICT behavior instead of CASCADE"},
            {"id": "c", "text": "The child foreign key values are updated to NULL", "correct": False, "maps_to": "D04", "misconception": "Describes ON DELETE SET NULL instead of CASCADE"},
            {"id": "d", "text": "The entire child table is dropped from the database", "correct": False, "maps_to": "D04", "misconception": "Exaggerates row-level cascade to a table drop"}
        ],
        "explanation": "ON DELETE CASCADE removes referencing child rows when the corresponding parent row is deleted.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_A_03",
        "concept": "D04",
        "family": "A",
        "difficulty": 2,
        "prompt": "Which SQL constraint enforces that employee salary must always be greater than zero?",
        "options": [
            {"id": "a", "text": "CHECK (salary > 0)", "correct": True},
            {"id": "b", "text": "UNIQUE (salary)", "correct": False, "maps_to": "D04", "misconception": "Confuses value uniqueness with numeric range validation"},
            {"id": "c", "text": "FOREIGN KEY (salary)", "correct": False, "maps_to": "D04", "misconception": "Confuses referential lookups with scalar check constraints"},
            {"id": "d", "text": "CASCADE (salary > 0)", "correct": False, "maps_to": "D04", "misconception": "CASCADE is a referential action modifier, not a predicate constraint"}
        ],
        "explanation": "CHECK constraints evaluate boolean expressions to enforce domain integrity rules.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_A_04",
        "concept": "D04",
        "family": "A",
        "difficulty": 3,
        "prompt": "If an UPDATE statement attempts to change a parent primary key, but a child row references it under ON UPDATE RESTRICT, what occurs?",
        "options": [
            {"id": "a", "text": "The DBMS rejects the update and raises a referential integrity violation error", "correct": True},
            {"id": "b", "text": "The DBMS updates the parent row and sets child foreign keys to 0", "correct": False, "maps_to": "D04", "misconception": "Believes RESTRICT modifies child values to zero"},
            {"id": "c", "text": "The DBMS automatically cascades the update to the child table", "correct": False, "maps_to": "D04", "misconception": "Confuses RESTRICT with CASCADE"},
            {"id": "d", "text": "The parent row is duplicated with both old and new primary keys", "correct": False, "maps_to": "D04", "misconception": "Primary key uniqueness prevents duplicate primary key values"}
        ],
        "explanation": "RESTRICT prevents modification of the parent key if referencing child rows exist.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_A_05",
        "concept": "D04",
        "family": "A",
        "difficulty": 2,
        "prompt": "What happens if an INSERT statement attempts to insert a duplicate value into a column with a UNIQUE constraint?",
        "options": [
            {"id": "a", "text": "The insertion is rejected by the DBMS with a uniqueness violation error", "correct": True},
            {"id": "b", "text": "The existing row is overwritten without notice", "correct": False, "maps_to": "D04", "misconception": "Confuses INSERT with an upsert/overwrite operation"},
            {"id": "c", "text": "The new row is saved into a temporary overflow table", "correct": False, "maps_to": "D01", "misconception": "Imagines overflow file storage rather than constraint rejection"},
            {"id": "d", "text": "The column value is automatically incremented by 1", "correct": False, "maps_to": "D03", "misconception": "Confuses auto-increment sequences with UNIQUE constraint handling"}
        ],
        "explanation": "A UNIQUE constraint prohibits duplicate values, causing violating statements to abort.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_A_06",
        "concept": "D04",
        "family": "A",
        "difficulty": 1,
        "prompt": "How does Domain Integrity differ from Referential Integrity?",
        "options": [
            {"id": "a", "text": "Domain integrity restricts values within a single attribute, while referential integrity coordinates relationships between tables", "correct": True},
            {"id": "b", "text": "Domain integrity applies only to string types, while referential integrity applies only to numbers", "correct": False, "maps_to": "D04", "misconception": "Arbitrarily assigns data types to constraint categories"},
            {"id": "c", "text": "Referential integrity operates only inside stored procedures", "correct": False, "maps_to": "D08", "misconception": "Misplaces declarative constraints into procedural code"},
            {"id": "d", "text": "Domain integrity requires two tables to be joined", "correct": False, "maps_to": "D09", "misconception": "Domain integrity applies to a single column/attribute"}
        ],
        "explanation": "Domain integrity applies to valid column values; referential integrity ensures cross-table key references remain valid.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_B_01",
        "concept": "D04",
        "family": "B",
        "difficulty": 1,
        "prompt": "A table Students has Primary Key StudentID. A query executes: INSERT INTO Students (StudentID, Name) VALUES (NULL, 'Alice'). What is the outcome?",
        "options": [
            {"id": "a", "text": "Rejected due to Entity Integrity violation", "correct": True},
            {"id": "b", "text": "Accepted and assigned StudentID 0", "correct": False, "maps_to": "D04", "misconception": "Assumes DBMS coerces NULL primary keys to integer 0"},
            {"id": "c", "text": "Accepted as a temporary record", "correct": False, "maps_to": "D04", "misconception": "Imagines temporary storage for invalid primary key rows"},
            {"id": "d", "text": "Rejected due to Referential Integrity violation", "correct": False, "maps_to": "D04", "misconception": "Primary key null checks are entity integrity, not referential integrity"}
        ],
        "explanation": "Entity Integrity forbids NULL primary key values, rejecting the insert.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_B_02",
        "concept": "D04",
        "family": "B",
        "difficulty": 2,
        "prompt": "Department 10 is deleted. Employees has DeptID defined as FOREIGN KEY REFERENCES Department(DeptID) ON DELETE SET NULL. What happens to employees in Dept 10?",
        "options": [
            {"id": "a", "text": "Their DeptID column is set to NULL while their employee rows remain", "correct": True},
            {"id": "b", "text": "Their employee rows are deleted from the database", "correct": False, "maps_to": "D04", "misconception": "Confuses SET NULL with CASCADE"},
            {"id": "c", "text": "Their DeptID is changed to DeptID 1", "correct": False, "maps_to": "D04", "misconception": "Assumes fallback to a default row rather than NULL"},
            {"id": "d", "text": "The deletion of Department 10 is blocked", "correct": False, "maps_to": "D04", "misconception": "Confuses SET NULL with RESTRICT"}
        ],
        "explanation": "ON DELETE SET NULL sets referencing columns to NULL when the referenced row is removed.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_B_03",
        "concept": "D04",
        "family": "B",
        "difficulty": 2,
        "prompt": "Can a column with a UNIQUE constraint accept multiple rows with NULL values in standard SQL?",
        "options": [
            {"id": "a", "text": "Yes, because under standard SQL logic, two NULLs do not equal each other and do not constitute duplicates", "correct": True},
            {"id": "b", "text": "No, UNIQUE constraints automatically forbid all NULL values", "correct": False, "maps_to": "D04", "misconception": "Confuses UNIQUE constraints with PRIMARY KEY (which enforces NOT NULL)"},
            {"id": "c", "text": "Only if the table is created with zero rows", "correct": False, "maps_to": "D04", "misconception": "Fabricates row count conditions on nullability rules"},
            {"id": "d", "text": "Only if the column data type is INTEGER", "correct": False, "maps_to": "D08", "misconception": "Restricts standard SQL null uniqueness to integer types"}
        ],
        "explanation": "In standard SQL, NULL != NULL. Multiple rows with NULL in a UNIQUE column do not violate uniqueness unless NOT NULL is also specified.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_B_04",
        "concept": "D04",
        "family": "B",
        "difficulty": 3,
        "prompt": "An architect designs an orders table where ShipDate cannot precede OrderDate. What constraint type best enforces this within a single table?",
        "options": [
            {"id": "a", "text": "Table-level CHECK constraint: CHECK (ShipDate >= OrderDate)", "correct": True},
            {"id": "b", "text": "Referential Integrity constraint referencing a Date table", "correct": False, "maps_to": "D04", "misconception": "Foreign keys enforce equality references, not comparison predicates across columns"},
            {"id": "c", "text": "Column-level UNIQUE constraint on ShipDate", "correct": False, "maps_to": "D03", "misconception": "Uniqueness prevents identical dates rather than ordering them"},
            {"id": "d", "text": "2-Phase Commit locking trigger", "correct": False, "maps_to": "D16", "misconception": "Confuses distributed consensus with declarative table checks"}
        ],
        "explanation": "A multi-column table CHECK constraint can compare values of two columns in the same row.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_B_05",
        "concept": "D04",
        "family": "B",
        "difficulty": 1,
        "prompt": "What occurs when an INSERT query attempts to add an order with CustomerID = 999, but no such customer exists in the referenced Customers table?",
        "options": [
            {"id": "a", "text": "Referential integrity violation error is thrown and insertion fails", "correct": True},
            {"id": "b", "text": "A dummy customer record with ID 999 is automatically inserted", "correct": False, "maps_to": "D04", "misconception": "Assumes DBMS automatically synthesizes parent records"},
            {"id": "c", "text": "CustomerID is set to 0 and row is inserted", "correct": False, "maps_to": "D04", "misconception": "DBMS does not overwrite foreign keys without explicit triggers"},
            {"id": "d", "text": "The entire database reverts to initial factory state", "correct": False, "maps_to": "D15", "misconception": "Exaggerates constraint failure to a catastrophic wipe"}
        ],
        "explanation": "Referential integrity forbids orphan records; every foreign key must reference a valid existing parent key.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D05: ER Modeling (11 questions)
    # ==========================================
    {
        "id": "Q_D05_A_01",
        "concept": "D05",
        "family": "A",
        "difficulty": 1,
        "prompt": "In an Entity-Relationship (ER) diagram, how is a weak entity type visually represented in standard Chen notation?",
        "options": [
            {"id": "a", "text": "A double rectangle", "correct": True},
            {"id": "b", "text": "A dashed ellipse", "correct": False, "maps_to": "D05", "misconception": "Dashed ellipses represent derived attributes"},
            {"id": "c", "text": "A double diamond", "correct": False, "maps_to": "D05", "misconception": "Double diamond represents identifying relationship, not the weak entity itself"},
            {"id": "d", "text": "An inverted triangle", "correct": False, "maps_to": "D05", "misconception": "Inverted triangle denotes generalization/specialization (ISA)"}
        ],
        "explanation": "In Chen's ER notation, weak entity types are represented by double rectangles, while identifying relationships use double diamonds.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_A_02",
        "concept": "D05",
        "family": "A",
        "difficulty": 2,
        "prompt": "What defines a weak entity in conceptual ER modeling?",
        "options": [
            {"id": "a", "text": "An entity that lacks a primary key of its own and depends on an identifying owner entity for existence", "correct": True},
            {"id": "b", "text": "An entity that has fewer than three attributes", "correct": False, "maps_to": "D05", "misconception": "Arbitrarily equates weak entity to small attribute count"},
            {"id": "c", "text": "An entity stored solely in temporary memory", "correct": False, "maps_to": "D01", "misconception": "Confuses entity classification with physical storage caching"},
            {"id": "d", "text": "An entity that participates only in M:N relationships", "correct": False, "maps_to": "D05", "misconception": "Weak entities participate in 1:N identifying relationships with their owner"}
        ],
        "explanation": "A weak entity does not possess sufficient attributes to form a primary key on its own; it requires a partial key (discriminator) combined with the owner entity's primary key.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_A_03",
        "concept": "D05",
        "family": "A",
        "difficulty": 2,
        "prompt": "In an ER diagram, an employee may have multiple phone numbers (e.g. Home, Mobile, Work). What kind of attribute is PhoneNumber?",
        "options": [
            {"id": "a", "text": "Multivalued attribute", "correct": True},
            {"id": "b", "text": "Derived attribute", "correct": False, "maps_to": "D05", "misconception": "Confuses multivalued attribute (represented by double ellipse) with derived attribute (dashed ellipse)"},
            {"id": "c", "text": "Composite attribute", "correct": False, "maps_to": "D05", "misconception": "Confuses composite attributes (divisible into parts) with multivalued attributes"},
            {"id": "d", "text": "Key attribute", "correct": False, "maps_to": "D03", "misconception": "A multivalued attribute cannot serve directly as a primary key"}
        ],
        "explanation": "A multivalued attribute can take multiple values for a single entity instance, represented in ER diagrams with a double ellipse.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_A_04",
        "concept": "D05",
        "family": "A",
        "difficulty": 1,
        "prompt": "How is a derived attribute represented in Chen ER notation?",
        "options": [
            {"id": "a", "text": "Dashed ellipse", "correct": True},
            {"id": "b", "text": "Double oval", "correct": False, "maps_to": "D05", "misconception": "Double oval represents multivalued attributes"},
            {"id": "c", "text": "Underlined rectangle", "correct": False, "maps_to": "D05", "misconception": "Underlined text represents primary key attributes"},
            {"id": "d", "text": "Hexagon", "correct": False, "maps_to": "D05", "misconception": "Hexagons are not standard Chen ER notation symbols"}
        ],
        "explanation": "A derived attribute (like Age computed from DateOfBirth) is depicted with a dashed ellipse.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_A_05",
        "concept": "D05",
        "family": "A",
        "difficulty": 3,
        "prompt": "What does total participation (represented by a double line) of entity E in relationship R signify?",
        "options": [
            {"id": "a", "text": "Every instance of entity E must participate in at least one relationship instance in R", "correct": True},
            {"id": "b", "text": "Entity E can participate at most once in R", "correct": False, "maps_to": "D05", "misconception": "Confuses participation constraint with cardinality ratio 1:1"},
            {"id": "c", "text": "Entity E has zero attributes", "correct": False, "maps_to": "D05", "misconception": "Participation has nothing to do with attribute counts"},
            {"id": "d", "text": "Entity E is a recursive relationship with itself", "correct": False, "maps_to": "D05", "misconception": "Confuses total participation with recursive relationships"}
        ],
        "explanation": "Total participation (existence dependency) mandates that every entity in the entity set must be related to an entity in the other set.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_A_06",
        "concept": "D05",
        "family": "A",
        "difficulty": 2,
        "prompt": "What is an attribute that can be divided into smaller sub-parts (e.g. Address divided into Street, City, ZipCode)?",
        "options": [
            {"id": "a", "text": "Composite attribute", "correct": True},
            {"id": "b", "text": "Multivalued attribute", "correct": False, "maps_to": "D05", "misconception": "Confuses composite attributes with multivalued attributes"},
            {"id": "c", "text": "Derived attribute", "correct": False, "maps_to": "D05", "misconception": "Confuses structural division with calculation from other attributes"},
            {"id": "d", "text": "Foreign attribute", "correct": False, "maps_to": "D04", "misconception": "No such ER attribute category as foreign attribute"}
        ],
        "explanation": "Composite attributes can be subdivided into independent components with their own semantic meanings.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_B_01",
        "concept": "D05",
        "family": "B",
        "difficulty": 1,
        "prompt": "In an ER model, how is the partial key (discriminator) of a weak entity represented?",
        "options": [
            {"id": "a", "text": "Dashed underline attribute name", "correct": True},
            {"id": "b", "text": "Solid underline attribute name", "correct": False, "maps_to": "D05", "misconception": "Solid underline indicates the primary key of a strong entity"},
            {"id": "c", "text": "Double underline attribute name", "correct": False, "maps_to": "D05", "misconception": "Double underlines are not standard ER notation"},
            {"id": "d", "text": "Bold italic text inside a circle", "correct": False, "maps_to": "D05", "misconception": "Styling variations are not standard Chen ER conventions"}
        ],
        "explanation": "The partial key (discriminator) of a weak entity is indicated with a dashed underline beneath the attribute name.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_B_02",
        "concept": "D05",
        "family": "B",
        "difficulty": 2,
        "prompt": "If every Department must have a Manager (total participation), but not every Employee is a Manager (partial participation), which side of the 'Manages' relationship has a double line?",
        "options": [
            {"id": "a", "text": "Department side", "correct": True},
            {"id": "b", "text": "Employee side", "correct": False, "maps_to": "D05", "misconception": "Reverses total and partial participation entities"},
            {"id": "c", "text": "Both sides", "correct": False, "maps_to": "D05", "misconception": "Double lines on both sides indicates total participation for both"},
            {"id": "d", "text": "Neither side", "correct": False, "maps_to": "D05", "misconception": "Overlooks the visual notation for total participation"}
        ],
        "explanation": "Since every Department must participate in 'Manages', Department exhibits total participation, depicted by a double line.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_B_03",
        "concept": "D05",
        "family": "B",
        "difficulty": 2,
        "prompt": "A university system has Students and Courses. A Student can take multiple Courses, and a Course can enroll multiple Students. What is the cardinality ratio?",
        "options": [
            {"id": "a", "text": "Many-to-Many (M:N)", "correct": True},
            {"id": "b", "text": "One-to-Many (1:N)", "correct": False, "maps_to": "D05", "misconception": "Ignores that courses have multiple students"},
            {"id": "c", "text": "One-to-One (1:1)", "correct": False, "maps_to": "D05", "misconception": "Assumes a student can only take a single course"},
            {"id": "d", "text": "Ternary recursive", "correct": False, "maps_to": "D05", "misconception": "Confuses binary cardinality with ternary relationship degree"}
        ],
        "explanation": "Since multiple instances on both sides can relate to multiple instances on the other, the cardinality ratio is Many-to-Many (M:N).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_B_04",
        "concept": "D05",
        "family": "B",
        "difficulty": 3,
        "prompt": "What is a recursive (or self-referencing) relationship in ER modeling?",
        "options": [
            {"id": "a", "text": "A relationship type where the same entity type participates more than once in distinct roles", "correct": True},
            {"id": "b", "text": "A relationship that executes infinite nested subqueries", "correct": False, "maps_to": "D11", "misconception": "Confuses database design relationships with SQL execution loops"},
            {"id": "c", "text": "A relationship linking four or more tables", "correct": False, "maps_to": "D05", "misconception": "Confuses degree of relationship with recursive role participation"},
            {"id": "d", "text": "A relationship between two database servers", "correct": False, "maps_to": "D01", "misconception": "Confuses data modeling with physical replication"}
        ],
        "explanation": "In a recursive relationship (such as 'ReportsTo' where Employee manages Employee), the same entity type plays different roles.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D05_B_05",
        "concept": "D05",
        "family": "B",
        "difficulty": 1,
        "prompt": "In ER diagrams, what does an ellipse directly attached to an entity rectangle represent?",
        "options": [
            {"id": "a", "text": "An attribute of the entity", "correct": True},
            {"id": "b", "text": "A relationship to another entity", "correct": False, "maps_to": "D05", "misconception": "Diamonds represent relationships, not ellipses"},
            {"id": "c", "text": "A primary key constraint index", "correct": False, "maps_to": "D17", "misconception": "Confuses physical indexes with conceptual attributes"},
            {"id": "d", "text": "A weak entity dependency", "correct": False, "maps_to": "D05", "misconception": "Double rectangles represent weak entities"}
        ],
        "explanation": "In Chen notation, attributes are represented by ellipses connected to their entity rectangle.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D06: ER-to-Relational Mapping (11 questions)
    # ==========================================
    {
        "id": "Q_D06_A_01",
        "concept": "D06",
        "family": "A",
        "difficulty": 1,
        "prompt": "When mapping a regular 1:N relationship from an ER model to relational tables, where should the foreign key be placed?",
        "options": [
            {"id": "a", "text": "In the relation representing the N-side (many-side) of the relationship", "correct": True},
            {"id": "b", "text": "In the relation representing the 1-side of the relationship", "correct": False, "maps_to": "D06", "misconception": "Placing FK on 1-side violates 1NF by requiring an array of child IDs"},
            {"id": "c", "text": "In a mandatory third junction table with a single column", "correct": False, "maps_to": "D06", "misconception": "A separate junction table is necessary for M:N, not 1:N"},
            {"id": "d", "text": "In both relations simultaneously", "correct": False, "maps_to": "D06", "misconception": "Dual foreign keys create mutual circular dependency anomalies"}
        ],
        "explanation": "In a 1:N relationship, each instance on the N-side relates to at most one on the 1-side. Hence, the N-side relation contains the foreign key.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_A_02",
        "concept": "D06",
        "family": "A",
        "difficulty": 2,
        "prompt": "How is a Many-to-Many (M:N) relationship between Students and Courses mapped to a relational schema?",
        "options": [
            {"id": "a", "text": "Create a separate relationship (junction) table containing foreign keys referencing both Students and Courses as a composite primary key", "correct": True},
            {"id": "b", "text": "Add a comma-separated string column of CourseIDs to the Students table", "correct": False, "maps_to": "D13", "misconception": "Violates First Normal Form atomic value requirements"},
            {"id": "c", "text": "Add a single StudentID column to the Courses table", "correct": False, "maps_to": "D06", "misconception": "Restricts courses to having only one student"},
            {"id": "d", "text": "Merge Students and Courses into one single wide table", "correct": False, "maps_to": "D13", "misconception": "Produces immense data redundancy and update anomalies"}
        ],
        "explanation": "An M:N relationship maps to an associative/junction table whose primary key is composed of the foreign keys of both participating entities.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_A_03",
        "concept": "D06",
        "family": "A",
        "difficulty": 2,
        "prompt": "How is a weak entity type Dependent (with partial key DepName and owner Employee with PK EmpID) mapped to a relation?",
        "options": [
            {"id": "a", "text": "A relation Dependent with composite primary key {EmpID, DepName}, where EmpID is also a foreign key", "correct": True},
            {"id": "b", "text": "A relation Dependent with DepName as the sole primary key", "correct": False, "maps_to": "D06", "misconception": "Partial key DepName is not globally unique without owner EmpID"},
            {"id": "c", "text": "Dependent attributes are merged directly as columns in Employee", "correct": False, "maps_to": "D13", "misconception": "Employees can have multiple dependents, violating 1NF"},
            {"id": "d", "text": "Dependent does not get mapped to any relational table", "correct": False, "maps_to": "D06", "misconception": "Weak entities must be mapped into relational tables"}
        ],
        "explanation": "The primary key of the weak entity relation becomes the combination of the owner entity's primary key (as a foreign key) and the partial key.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_A_04",
        "concept": "D06",
        "family": "A",
        "difficulty": 2,
        "prompt": "How is a multivalued attribute, such as Skills for an Employee(EmpID), mapped into the relational model to adhere to 1NF?",
        "options": [
            {"id": "a", "text": "Create a new relation Employee_Skills(EmpID, Skill) with composite primary key {EmpID, Skill}", "correct": True},
            {"id": "b", "text": "Create 50 separate columns Skill1, Skill2, ..., Skill50 in the Employee table", "correct": False, "maps_to": "D13", "misconception": "Creates repeating groups and sparse null values"},
            {"id": "c", "text": "Store all skills as an unparsed JSON array string in a single column", "correct": False, "maps_to": "D02", "misconception": "Abandons relational modeling normalization principles"},
            {"id": "d", "text": "Drop the Skills attribute entirely from the schema", "correct": False, "maps_to": "D06", "misconception": "Data attributes must be modeled in tables"}
        ],
        "explanation": "A multivalued attribute maps to a new relation containing the attribute and the entity's primary key (as a foreign key), forming a composite primary key.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_A_05",
        "concept": "D06",
        "family": "A",
        "difficulty": 3,
        "prompt": "When mapping a 1:1 relationship between Employee and Workstation, where participation is total for Workstation but partial for Employee, what is the cleanest design?",
        "options": [
            {"id": "a", "text": "Place the foreign key EmpID inside the Workstation table with a NOT NULL constraint", "correct": True},
            {"id": "b", "text": "Place the foreign key WorkstationID inside the Employee table with frequent NULLs", "correct": False, "maps_to": "D06", "misconception": "Causes excessive NULL values since employee participation is partial"},
            {"id": "c", "text": "Create two junction tables linking Employee and Workstation", "correct": False, "maps_to": "D06", "misconception": "Unnecessary overhead for a 1:1 relationship"},
            {"id": "d", "text": "Merge Employee and Workstation into a single unified table", "correct": False, "maps_to": "D06", "misconception": "Mixes distinct entities and forces nulls for employees without workstations"}
        ],
        "explanation": "Placing the foreign key on the total participation side (Workstation) guarantees no NULLs are introduced in the foreign key column.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_A_06",
        "concept": "D06",
        "family": "A",
        "difficulty": 1,
        "prompt": "How is a composite attribute, like Name(FirstName, LastName), mapped into a relational table?",
        "options": [
            {"id": "a", "text": "Flatten it into its simple component attributes: FirstName and LastName columns in the relation", "correct": True},
            {"id": "b", "text": "Create a separate Name table with an artificial NameID foreign key", "correct": False, "maps_to": "D06", "misconception": "Unnecessary table decomposition for simple composite attributes"},
            {"id": "c", "text": "Store both values concatenated with no delimiter in a single column", "correct": False, "maps_to": "D02", "misconception": "Violates attribute clarity and retrieval ergonomics"},
            {"id": "d", "text": "Discard LastName and only store FirstName", "correct": False, "maps_to": "D06", "misconception": "Causes data loss"}
        ],
        "explanation": "Composite attributes are mapped by including only their simple component attributes as columns in the relation.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_B_01",
        "concept": "D06",
        "family": "B",
        "difficulty": 1,
        "prompt": "In an ER diagram, Department has a 1:N relationship with Employee (one Department has many Employees). Which relational table holds the DeptID foreign key?",
        "options": [
            {"id": "a", "text": "Employee", "correct": True},
            {"id": "b", "text": "Department", "correct": False, "maps_to": "D06", "misconception": "Placing foreign key on the 1-side requires repeating groups or array values"},
            {"id": "c", "text": "A separate Dept_Emp junction table is strictly required", "correct": False, "maps_to": "D06", "misconception": "Junction tables are required for M:N relationships, not 1:N"},
            {"id": "d", "text": "Both Employee and Department", "correct": False, "maps_to": "D06", "misconception": "Mutual foreign keys create circular reference problems"}
        ],
        "explanation": "In 1:N relationships, the foreign key referencing the 1-side is stored in the table representing the N-side (Employee).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_B_02",
        "concept": "D06",
        "family": "B",
        "difficulty": 2,
        "prompt": "An M:N relationship 'Enrollment' between Student(StudentID) and Course(CourseID) also has an attribute 'Grade'. Where is 'Grade' placed in the relational schema?",
        "options": [
            {"id": "a", "text": "In the Enrollment junction table alongside StudentID and CourseID", "correct": True},
            {"id": "b", "text": "In the Student table", "correct": False, "maps_to": "D06", "misconception": "Grade is specific to a course enrollment, not the student globally"},
            {"id": "c", "text": "In the Course table", "correct": False, "maps_to": "D06", "misconception": "Grade is specific to an individual student, not the course globally"},
            {"id": "d", "text": "In a separate single-column Grade table", "correct": False, "maps_to": "D06", "misconception": "Isolating Grade from the enrollment key destroys association"}
        ],
        "explanation": "Attributes of an M:N relationship are placed directly in the junction relation representing that relationship.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_B_03",
        "concept": "D06",
        "family": "B",
        "difficulty": 2,
        "prompt": "A Building weak entity has partial key RoomNumber and owner Hotel(HotelID). What is the primary key of the Room table?",
        "options": [
            {"id": "a", "text": "{HotelID, RoomNumber}", "correct": True},
            {"id": "b", "text": "RoomNumber alone", "correct": False, "maps_to": "D06", "misconception": "RoomNumber is not unique across different hotels"},
            {"id": "c", "text": "HotelID alone", "correct": False, "maps_to": "D06", "misconception": "A hotel has multiple rooms, violating primary key uniqueness"},
            {"id": "d", "text": "No primary key is required for weak entity tables", "correct": False, "maps_to": "D04", "misconception": "All relational base tables require primary keys under entity integrity"}
        ],
        "explanation": "The composite primary key combines the identifying owner's primary key (HotelID) with the weak entity's partial key (RoomNumber).",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_B_04",
        "concept": "D06",
        "family": "B",
        "difficulty": 3,
        "prompt": "Why is mapping an M:N relationship by embedding foreign key arrays directly into one of the base tables considered a violation of relational theory?",
        "options": [
            {"id": "a", "text": "It violates First Normal Form by storing non-atomic multivalued lists in a single cell", "correct": True},
            {"id": "b", "text": "It prevents SQL compilers from generating binary executable code", "correct": False, "maps_to": "D08", "misconception": "Fabricates compilation issues rather than recognizing 1NF violation"},
            {"id": "c", "text": "It forces all primary keys to convert to floating-point numbers", "correct": False, "maps_to": "D02", "misconception": "Irrelevant data type speculation"},
            {"id": "d", "text": "It disables transactions across the entire DBMS", "correct": False, "maps_to": "D15", "misconception": "Transactions remain operational regardless of schema design"}
        ],
        "explanation": "Storing arrays or lists of foreign keys in a single row violates 1NF (atomicity rule) and makes querying and integrity enforcement cumbersome.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D06_B_05",
        "concept": "D06",
        "family": "B",
        "difficulty": 1,
        "prompt": "When mapping an ER model into relational tables, what does an Entity Type typically become?",
        "options": [
            {"id": "a", "text": "A relation (table)", "correct": True},
            {"id": "b", "text": "A column (attribute)", "correct": False, "maps_to": "D06", "misconception": "Entity types become relations; entity attributes become columns"},
            {"id": "c", "text": "A stored procedure", "correct": False, "maps_to": "D08", "misconception": "Confuses structural data tables with procedural routines"},
            {"id": "d", "text": "A B+ Tree root node", "correct": False, "maps_to": "D17", "misconception": "Confuses relational mapping with index node structures"}
        ],
        "explanation": "In standard ER-to-Relational mapping, each strong entity type maps directly to a relation (table).",
        "validation_status": "reviewed"
    }
]
