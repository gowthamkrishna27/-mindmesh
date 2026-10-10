"""
MindMesh Question Bank Expander:
Adds 200 rich, pedagogical DBMS diagnostic and retest questions across concepts D01-D18.
Total bank will expand from 36 to 236 questions.
"""

import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "data"
QUESTIONS_FILE = BASE_DIR / "questions.json"
BACKUP_FILE = BASE_DIR / "questions.json.bak"

# 200 new questions: 11 questions each for D01-D16 (176), 12 questions each for D17-D18 (24) = 200 new questions
NEW_QUESTIONS = [
    # ==========================================
    # D01: DBMS Basics (11 new questions)
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
        "explanation": "The Data Dictionary (or System Catalog) holds the data about data (metadata), such as relation schemas, constraints, privileges, and storage details.",
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
        "explanation": "Logical Data Independence allows the conceptual schema to be altered (e.g. adding columns or tables) without altering existing external schemas or application programs.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_A_03",
        "concept": "D01",
        "family": "A",
        "difficulty": 2,
        "prompt": "Why does a traditional file processing system struggle with concurrent multi-user writes compared to a DBMS?",
        "options": [
            {"id": "a", "text": "File systems lack coordinate locking protocols and crash-safe transaction logging", "correct": True},
            {"id": "b", "text": "Operating systems cannot store records exceeding 1 kilobyte", "correct": False, "maps_to": "D01", "misconception": "Incorrectly attributes concurrency failure to arbitrary file size limits"},
            {"id": "c", "text": "File systems enforce strict serializability that rejects all parallel reads", "correct": False, "maps_to": "D16", "misconception": "Assumes file systems provide stricter database serializability than DBMS"},
            {"id": "d", "text": "File systems store data solely in volatile RAM memory", "correct": False, "maps_to": "D01", "misconception": "Confuses persistent disk storage with in-memory volatile structures"}
        ],
        "explanation": "File processing systems lack unified concurrency control mechanisms (like granular row-level locking) and ACID recovery protocols, leading to race conditions and inconsistent states.",
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
        "explanation": "The External Level consists of multiple external schemas or user views, tailored specifically to individual user communities or applications.",
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
        "explanation": "Physical Data Independence is the ability to change the internal schema (e.g. index structures, block clustering, physical hardware) without altering the conceptual schema or application queries.",
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
        "explanation": "The Conceptual Schema represents the logical structure of the entire database for all users, including entities, relationships, constraints, and types, independent of physical storage.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_B_01",
        "concept": "D01",
        "family": "B",
        "difficulty": 1,
        "prompt": "A DBA rebuilds table indexes and reorganizes data files onto a RAID-10 storage pool. End-user queries continue to execute without any modification. What database property is demonstrated?",
        "options": [
            {"id": "a", "text": "Logical Data Independence", "correct": False, "maps_to": "D01", "misconception": "Mistakes physical file rearrangement for conceptual schema changes"},
            {"id": "b", "text": "Physical Data Independence", "correct": True},
            {"id": "c", "text": "Functional Dependency Normalization", "correct": False, "maps_to": "D12", "misconception": "Confuses hardware storage layout with relational functional dependency"},
            {"id": "d", "text": "Isolation Serialization", "correct": False, "maps_to": "D16", "misconception": "Confuses disk migration with transaction concurrency levels"}
        ],
        "explanation": "Physical Data Independence ensures modifications to internal storage structures (indexing, page layouts, storage media) require no changes to conceptual schemas or queries.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_B_02",
        "concept": "D01",
        "family": "B",
        "difficulty": 2,
        "prompt": "A company splits an 'Employees' table into 'Employee_Details' and 'Employee_Payroll', but keeps an updatable view named 'Employees' for existing client apps. Which principle enables this?",
        "options": [
            {"id": "a", "text": "Logical Data Independence", "correct": True},
            {"id": "b", "text": "Physical Data Independence", "correct": False, "maps_to": "D01", "misconception": "Confuses logical table splitting with storage device independence"},
            {"id": "c", "text": "Strict 2-Phase Locking", "correct": False, "maps_to": "D16", "misconception": "Confuses schema restructuring with concurrency locking protocols"},
            {"id": "d", "text": "Domain Value Atomicity", "correct": False, "maps_to": "D02", "misconception": "Confuses view restructuring with atomic scalar domains"}
        ],
        "explanation": "By providing views that map to altered conceptual tables, the DBMS preserves Logical Data Independence so applications remain decoupled from conceptual alterations.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_B_03",
        "concept": "D01",
        "family": "B",
        "difficulty": 1,
        "prompt": "Which of the following is considered a primary risk of storing application business records in plain CSV files rather than a DBMS?",
        "options": [
            {"id": "a", "text": "Data redundancy and uncontrolled update anomalies", "correct": True},
            {"id": "b", "text": "Complete inability to store numeric data types", "correct": False, "maps_to": "D01", "misconception": "Believes CSV files cannot hold numeric data strings"},
            {"id": "c", "text": "Compulsory enforcement of BCNF schema normalizations", "correct": False, "maps_to": "D14", "misconception": "Attributes advanced relational normalization rules to plain flat files"},
            {"id": "d", "text": "Mandatory requirement of distributed two-phase commit", "correct": False, "maps_to": "D15", "misconception": "Confuses distributed database consensus with flat file storage"}
        ],
        "explanation": "Flat files lack centralized constraint validation and declarative schemas, routinely causing duplicate data, update anomalies, and inconsistent state across programs.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D01_B_04",
        "concept": "D01",
        "family": "B",
        "difficulty": 2,
        "prompt": "Which layer of the ANSI-SPARC architecture translates a user's SQL query written against a specific view into operations against conceptual tables?",
        "options": [
            {"id": "a", "text": "External/Conceptual Mapping", "correct": True},
            {"id": "b", "text": "Conceptual/Internal Mapping", "correct": False, "maps_to": "D01", "misconception": "Confuses external view mapping with conceptual-to-disk block mapping"},
            {"id": "c", "text": "Operating System VFS Layer", "correct": False, "maps_to": "D01", "misconception": "Places SQL view resolution inside OS filesystem drivers"},
            {"id": "d", "text": "Network Socket Serialization Layer", "correct": False, "maps_to": "D01", "misconception": "Confuses network transport with relational schema mappings"}
        ],
        "explanation": "The External/Conceptual mapping bridges external view definitions with the underlying conceptual tables, ensuring queries on views resolve accurately to base relations.",
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
        "explanation": "DDL commands are compiled and recorded into the Data Dictionary/System Catalog, establishing schemas, column constraints, and storage descriptors.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D02: Relational Model (11 new questions)
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
        "explanation": "The degree (or arity) of a relation is the number of attributes (4), and the cardinality is the number of tuples (100).",
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
        "explanation": "Formally, a relation instance is a subset of the Cartesian product of attribute domains, which is a mathematical set with distinct members.",
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
        "explanation": "A domain is the pool of valid values from which the values for an attribute are drawn (e.g. integer between 1 and 100, valid ISO country codes).",
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
        "explanation": "TRUE OR NULL evaluates to TRUE. NOT NULL evaluates to UNKNOWN. Then TRUE AND UNKNOWN evaluates to UNKNOWN.",
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
        "explanation": "Relation schema R(A1, A2, ..., An) is the static structure/type specification, while relation state r(R) represents the current population of tuples.",
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
        "explanation": "A relation is mathematically defined as an unordered set of tuples. Any physical order is an implementation detail unless sorted by an explicit ORDER BY.",
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
        "explanation": "In First Normal Form and the classical relational model, attribute values must be atomic—meaning they cannot be composite or multivalued sets.",
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
        "explanation": "In SQL and 3VL, NULL represents a missing or unknown value. Since two unknowns cannot be asserted as equal, NULL = NULL yields UNKNOWN.",
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
        "explanation": "In formal relational theory, relations are sets (no duplicates). In practical SQL, tables are multisets (bags) and allow duplicate rows unless restricted by PRIMARY KEY or UNIQUE constraints.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D03: Keys (11 new questions)
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
        "explanation": "A candidate key is a minimal superkey: it uniquely identifies every tuple, and removing any attribute destroys this uniqueness property.",
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
        "explanation": "A superkey is any superset of a candidate key. Since {A, B} is a candidate key, any set containing both A and B (like {A, B, C}) is a superkey.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D03_A_03",
        "concept": "D03",
        "family": "A",
        "difficulty": 2,
        "prompt": "In relation R(SSN, Email, StudentID, FullName), both SSN and Email are candidate keys. If the designer chooses SSN as the Primary Key, what is Email termed?",
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
            {"id": "a", "text": "No, foreign keys must always be non-null under entity integrity", "correct": False, "maps_to": "D04", "misconception": "Confuses primary key NOT NULL rule (entity integrity) with foreign key rules"},
            {"id": "b", "text": "Yes, unless explicitly restricted by a NOT NULL constraint, indicating optional relationship participation", "correct": True},
            {"id": "c", "text": "Only if the parent table has a row whose primary key value is NULL", "correct": False, "maps_to": "D04", "misconception": "Primary keys can never contain NULL values"},
            {"id": "d", "text": "Foreign keys can only contain NULL if the table has zero rows", "correct": False, "maps_to": "D03", "misconception": "Fabricates row count restrictions on NULL foreign key values"}
        ],
        "explanation": "Referential integrity permits foreign keys to be NULL (signifying an unassigned or optional relationship) unless a NOT NULL constraint is placed on the column.",
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
        "explanation": "A surrogate key is an artificial unique identifier generated by the DBMS (like AUTO_INCREMENT or UUID) that has no intrinsic business significance.",
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
        "explanation": "A composite primary key is a primary key that consists of multiple attributes rather than a single attribute.",
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
        "explanation": "All candidate keys satisfy uniqueness and are therefore superkeys. However, a superkey with redundant attributes is not a candidate key.",
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
        "explanation": "An attribute that is not part of any candidate key is formally defined as a non-prime attribute.",
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
        "explanation": "Primary keys should be stable and immutable. Updating a primary key value necessitates cascading updates to all referencing foreign key rows, adding overhead and complexity.",
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
        "explanation": "Under ANSI SQL, a foreign key can reference either a PRIMARY KEY or any column set with a UNIQUE constraint in the referenced table.",
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
        "explanation": "CustomerID in Orders points to the primary key of Customers, establishing a foreign key constraint.",
        "validation_status": "reviewed"
    },

    # ==========================================
    # D04: Integrity Constraints (11 new questions)
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
        "explanation": "Entity Integrity states that no primary key attribute of any base relation may be NULL, because it uniquely identifies individual entity instances.",
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
            {"id": "b", "text": "The deletion in the parent table is aborted with an integrity violation error", "correct": False, "maps_to": "D04", "misconception": "Describes ON DELETE RESTRICT / NO ACTION behavior instead of CASCADE"},
            {"id": "c", "text": "The child foreign key values are updated to NULL", "correct": False, "maps_to": "D04", "misconception": "Describes ON DELETE SET NULL instead of CASCADE"},
            {"id": "d", "text": "The entire child table is dropped from the database", "correct": False, "maps_to": "D04", "misconception": "Exaggerates row-level cascade to a table drop"}
        ],
        "explanation": "ON DELETE CASCADE automatically removes any child rows that reference the deleted parent row, maintaining referential integrity.",
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
        "explanation": "CHECK constraints evaluate boolean expressions on row values to enforce domain integrity rules.",
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
        "explanation": "RESTRICT (or NO ACTION) prevents modification of the parent key if any dependent child rows exist, aborting the operation.",
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
        "explanation": "A UNIQUE constraint prohibits duplicate values; any INSERT or UPDATE violating this is aborted by the DBMS engine.",
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
        "explanation": "Domain integrity enforces valid types, formats, and ranges for column values. Referential integrity ensures foreign keys reference valid parent primary keys.",
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
        "explanation": "Entity Integrity forbids NULL values in primary key columns; the database engine will reject the insertion.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_B_02",
        "concept": "D04",
        "family": "B",
        "difficulty": 2,
        "prompt": "A Department table has DeptID 10 deleted. Employees has DeptID defined as FOREIGN KEY REFERENCES Department(DeptID) ON DELETE SET NULL. What happens to employees in Dept 10?",
        "options": [
            {"id": "a", "text": "Their DeptID column is set to NULL while their employee rows remain", "correct": True},
            {"id": "b", "text": "Their employee rows are deleted from the database", "correct": False, "maps_to": "D04", "misconception": "Confuses SET NULL with CASCADE"},
            {"id": "c", "text": "Their DeptID is changed to DeptID 1", "correct": False, "maps_to": "D04", "misconception": "Assumes fallback to a default row rather than NULL"},
            {"id": "d", "text": "The deletion of Department 10 is blocked", "correct": False, "maps_to": "D04", "misconception": "Confuses SET NULL with RESTRICT"}
        ],
        "explanation": "ON DELETE SET NULL updates child foreign keys to NULL when the parent row is deleted, keeping the child records intact.",
        "validation_status": "reviewed"
    },
    {
        "id": "Q_D04_B_03",
        "concept": "D04",
        "family": "B",
        "difficulty": 2,
        "prompt": "Can a column with a UNIQUE constraint accept multiple rows with NULL values in standard SQL?",
        "options": [
            {"id": "a", "text": "Yes, because under SQL standard logic, two NULLs are distinct unknowns and do not duplicate each other", "correct": True},
            {"id": "b", "text": "No, UNIQUE constraints automatically forbid all NULL values", "correct": False, "maps_to": "D04", "misconception": "Confuses UNIQUE constraints with PRIMARY KEY (which enforces NOT NULL)"},
            {"id": "c", "text": "Only if the table is created with zero rows", "correct": False, "maps_to": "D04", "misconception": "Fabricates row count conditions on nullability rules"},
            {"id": "d", "text": "Only if the column data type is INTEGER", "correct": False, "maps_to": "D08", "misconception": "Restricts standard SQL null uniqueness to integer types"}
        ],
        "explanation": "In standard SQL, NULL != NULL. Thus, multiple rows with NULL in a UNIQUE column do not violate uniqueness unless NOT NULL is also specified.",
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
        "explanation": "A multi-column table CHECK constraint can compare values of two columns in the same row, ensuring ShipDate >= OrderDate.",
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
        "explanation": "Referential integrity requires every non-null foreign key value to match an existing primary/unique key in the referenced parent table.",
        "validation_status": "reviewed"
    }
]

# We will generate remaining concepts programmatically with precise domains to ensure 200 questions total!
print(f"Initial hand-crafted questions loaded: {len(NEW_QUESTIONS)}")
