export interface Concept {
  id: string;
  name: string;
  description: string;
  difficulty: number;
  learning_objectives: string[];
  prerequisites: string[];
  resources: {
    title: string;
    url: string;
    summary: string;
  }[];
  // Node coordinates for graph visualization
  x: number;
  y: number;
  tier: number;
}

export interface QuestionOption {
  id: string;
  text: string;
  correct: boolean;
  maps_to?: string;
  misconception?: string;
}

export interface Question {
  id: string;
  concept: string;
  family: 'A' | 'B';
  difficulty: number;
  prompt: string;
  options: QuestionOption[];
  explanation: string;
  validation_status: 'draft' | 'reviewed';
}

export interface StudentMastery {
  concept_id: string;
  p: number; // Mastery estimate (0.02 to 0.98)
  n_direct: number;
  n_indirect: number;
  status: 'insufficient' | 'suspected' | 'confirmed' | 'rejected' | 'mastered';
  blocker_score?: number;
  uncertainty?: number;
}

export interface ResponseRecord {
  id: string;
  question_id: string;
  concept_id: string;
  option_id: string;
  correct: boolean;
  confidence: 'low' | 'medium' | 'high';
  response_ms: number;
  evidence_weight: number;
  distractor_mapped_to?: string;
  misconception?: string;
  timestamp: string;
}

export interface LearningPathItem {
  id: string;
  position: number;
  concept_id: string;
  concept_name: string;
  rationale: string;
  completed: boolean;
  estimated_mins: number;
  key_takeaways: string[];
  practice_prompt: string;
  practice_solution: string;
}

export const CONCEPTS: Concept[] = [
  {
    id: "D01",
    name: "DBMS Basics",
    description: "Foundational concepts: data independence, 3-tier schema architecture, and DBMS vs file system distinctions.",
    difficulty: 1,
    learning_objectives: [
      "Distinguish file systems from DBMS",
      "Understand 3-tier schema architecture (Internal, Conceptual, External)",
      "Define logical and physical data independence"
    ],
    prerequisites: [],
    resources: [
      {
        title: "DBMS Architecture & Three-Schema Framework",
        url: "https://en.wikipedia.org/wiki/Database#Database_management_system",
        summary: "Detailed overview of database schemas, abstraction levels, and independence."
      }
    ],
    x: 50,
    y: 220,
    tier: 1
  },
  {
    id: "D02",
    name: "Relational Model",
    description: "Tabular representation of data, relation schemas, tuples, attributes, domains, and relational characteristics.",
    difficulty: 1,
    learning_objectives: [
      "Understand relations as sets of tuples",
      "Define attribute domains and null value semantics",
      "Distinguish between relation schema and relation state"
    ],
    prerequisites: ["D01"],
    resources: [
      {
        title: "Relational Model Core Theory",
        url: "https://en.wikipedia.org/wiki/Relational_model",
        summary: "E.F. Codd's foundational relational definitions and constraints."
      }
    ],
    x: 210,
    y: 220,
    tier: 2
  },
  {
    id: "D03",
    name: "Keys",
    description: "Key definitions and identification: superkeys, candidate keys, primary keys, and foreign keys.",
    difficulty: 2,
    learning_objectives: [
      "Distinguish superkeys from minimal candidate keys",
      "Identify primary key criteria",
      "Understand referential integrity constraints via foreign keys"
    ],
    prerequisites: ["D02"],
    resources: [
      {
        title: "Database Keys & Foreign Key Integrity",
        url: "https://en.wikipedia.org/wiki/Candidate_key",
        summary: "Minimal candidate keys, uniqueness, and referential constraints."
      }
    ],
    x: 380,
    y: 150,
    tier: 3
  },
  {
    id: "D04",
    name: "Integrity Constraints",
    description: "Domain constraints, entity integrity, referential integrity, and check constraints.",
    difficulty: 2,
    learning_objectives: [
      "Enforce entity integrity (primary keys cannot be null)",
      "Specify foreign key actions (CASCADE, SET NULL, RESTRICT)",
      "Formulate domain and check constraints"
    ],
    prerequisites: ["D02", "D03"],
    resources: [
      {
        title: "Data Integrity & Constraints",
        url: "https://en.wikipedia.org/wiki/Data_integrity",
        summary: "Preventing data corruption through declarative constraint checking."
      }
    ],
    x: 550,
    y: 70,
    tier: 4
  },
  {
    id: "D05",
    name: "ER Modeling",
    description: "Entity-Relationship modeling: entity sets, relationship types, cardinalities (1:1, 1:N, M:N), and weak entities.",
    difficulty: 2,
    learning_objectives: [
      "Construct ER diagrams with entity and relationship sets",
      "Specify structural constraints (cardinality ratios, participation)",
      "Model weak entity sets with identifying relationships"
    ],
    prerequisites: ["D01"],
    resources: [
      {
        title: "Conceptual ER Modeling",
        url: "https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model",
        summary: "Representing real-world requirements as ER conceptual diagrams."
      }
    ],
    x: 210,
    y: 80,
    tier: 2
  },
  {
    id: "D06",
    name: "ER-to-Relational Mapping",
    description: "Algorithms for mapping conceptual ER schemas into relational tables, handling complex cardinalities and weak entities.",
    difficulty: 3,
    learning_objectives: [
      "Translate regular and weak entity sets into tables",
      "Map 1:1, 1:N, and M:N relationships",
      "Decompose multivalued attributes into distinct relations"
    ],
    prerequisites: ["D05", "D03"],
    resources: [
      {
        title: "7-Step ER to Relational Mapping",
        url: "https://en.wikipedia.org/wiki/Relational_model#Mapping_from_ER_model",
        summary: "Step-by-step algorithms converting ER diagrams into normalized relational DDL."
      }
    ],
    x: 550,
    y: 140,
    tier: 4
  },
  {
    id: "D07",
    name: "Relational Algebra",
    description: "Procedural query language: Selection (σ), Projection (π), Union (∪), Set Difference (-), Cartesian Product (×), and Join (⨝).",
    difficulty: 3,
    learning_objectives: [
      "Evaluate unary operations: select and project",
      "Execute binary set operations and Cartesian product",
      "Compose complex relational algebra expressions with theta and natural joins"
    ],
    prerequisites: ["D02"],
    resources: [
      {
        title: "Relational Algebra Fundamentals",
        url: "https://en.wikipedia.org/wiki/Relational_algebra",
        summary: "Theoretical query operators and algebra equivalences."
      }
    ],
    x: 380,
    y: 240,
    tier: 3
  },
  {
    id: "D08",
    name: "SQL Basics",
    description: "Structured Query Language foundations: DDL (CREATE, ALTER, DROP) and DML (SELECT, INSERT, UPDATE, DELETE, WHERE).",
    difficulty: 2,
    learning_objectives: [
      "Formulate DDL table definitions with constraints",
      "Write SELECT-FROM-WHERE query filters",
      "Handle three-valued logic (TRUE, FALSE, UNKNOWN) with NULLs"
    ],
    prerequisites: ["D02"],
    resources: [
      {
        title: "SQL Basics and Query Syntax",
        url: "https://en.wikipedia.org/wiki/SQL",
        summary: "Core DDL/DML syntax and query evaluation pipeline."
      }
    ],
    x: 380,
    y: 320,
    tier: 3
  },
  {
    id: "D09",
    name: "SQL Joins",
    description: "Combining relational datasets: INNER JOIN, LEFT/RIGHT/FULL OUTER JOIN, and CROSS JOIN.",
    difficulty: 3,
    learning_objectives: [
      "Write multi-table inner joins with ON predicates",
      "Distinguish outer joins and handle NULL padding",
      "Avoid unintended Cartesian products"
    ],
    prerequisites: ["D08", "D07"],
    resources: [
      {
        title: "SQL Joins Visual Guide",
        url: "https://en.wikipedia.org/wiki/Join_(SQL)",
        summary: "Visual explanation of inner, left, right, and full outer joins."
      }
    ],
    x: 550,
    y: 290,
    tier: 4
  },
  {
    id: "D10",
    name: "Aggregation & GROUP BY",
    description: "Aggregate functions (COUNT, SUM, AVG, MIN, MAX), GROUP BY partitions, and HAVING clause filters.",
    difficulty: 3,
    learning_objectives: [
      "Calculate summary statistics across rows",
      "Partition datasets with GROUP BY",
      "Differentiate row filtering (WHERE) vs group filtering (HAVING)"
    ],
    prerequisites: ["D08"],
    resources: [
      {
        title: "SQL Aggregation and Grouping",
        url: "https://en.wikipedia.org/wiki/Aggregate_function",
        summary: "Group-level computations and HAVING predicates."
      }
    ],
    x: 550,
    y: 370,
    tier: 4
  },
  {
    id: "D11",
    name: "Subqueries and Views",
    description: "Nested queries, scalar subqueries, correlated subqueries, EXISTS/IN predicates, and virtual tables (views).",
    difficulty: 4,
    learning_objectives: [
      "Write correlated and non-correlated subqueries",
      "Utilize EXISTS, NOT EXISTS, IN, and ALL/ANY operators",
      "Define views for data abstraction and security"
    ],
    prerequisites: ["D08", "D09"],
    resources: [
      {
        title: "Subqueries & Correlated Nested Queries",
        url: "https://en.wikipedia.org/wiki/Correlated_subquery",
        summary: "Nested query execution semantics and view virtual tables."
      }
    ],
    x: 720,
    y: 370,
    tier: 5
  },
  {
    id: "D12",
    name: "Functional Dependencies",
    description: "Functional dependencies X → Y, Armstrong's axioms (reflexivity, augmentation, transitivity), and attribute closure X+.",
    difficulty: 3,
    learning_objectives: [
      "Define and interpret functional dependencies X → Y",
      "Compute attribute closure (X+) under a given set of FDs",
      "Determine all candidate keys using attribute closure"
    ],
    prerequisites: ["D03"],
    resources: [
      {
        title: "Functional Dependencies & Attribute Closure",
        url: "https://en.wikipedia.org/wiki/Functional_dependency",
        summary: "Armstrong's axioms, closure algorithm, and minimal covers."
      }
    ],
    x: 550,
    y: 210,
    tier: 4
  },
  {
    id: "D13",
    name: "Normalization (1NF to 3NF)",
    description: "Database normalization to eliminate redundancy and update anomalies: First Normal Form, Second Normal Form, and Third Normal Form.",
    difficulty: 4,
    learning_objectives: [
      "Ensure 1NF (atomic attributes, no repeating groups)",
      "Eliminate partial dependencies on candidate keys for 2NF",
      "Eliminate transitive dependencies for 3NF"
    ],
    prerequisites: ["D12", "D03"],
    resources: [
      {
        title: "Relational Normalization (1NF through 3NF)",
        url: "https://en.wikipedia.org/wiki/Database_normalization",
        summary: "Step-by-step normal form testing and anomaly elimination."
      }
    ],
    x: 720,
    y: 210,
    tier: 5
  },
  {
    id: "D14",
    name: "BCNF and Decomposition",
    description: "Boyce-Codd Normal Form, lossless-join decomposition testing, and dependency preservation properties.",
    difficulty: 4,
    learning_objectives: [
      "Evaluate BCNF condition (every determinant must be a superkey)",
      "Apply lossless-join decomposition algorithm",
      "Analyze dependency preservation trade-offs between 3NF and BCNF"
    ],
    prerequisites: ["D13"],
    resources: [
      {
        title: "Boyce-Codd Normal Form & Lossless Decomposition",
        url: "https://en.wikipedia.org/wiki/Boyce%E2%80%93Codd_normal_form",
        summary: "BCNF decomposition algorithms and property preservation."
      }
    ],
    x: 890,
    y: 210,
    tier: 6
  },
  {
    id: "D15",
    name: "Transactions and ACID",
    description: "Transaction concepts, transaction states, and ACID properties (Atomicity, Consistency, Isolation, Durability).",
    difficulty: 3,
    learning_objectives: [
      "Define transaction states: active, committed, aborted",
      "Explain ACID properties and recovery requirements",
      "Identify concurrent anomalies (dirty reads, non-repeatable reads, phantoms)"
    ],
    prerequisites: ["D01"],
    resources: [
      {
        title: "ACID Properties & Transaction Processing",
        url: "https://en.wikipedia.org/wiki/ACID",
        summary: "Transaction state transitions, logging, and durability guarantees."
      }
    ],
    x: 210,
    y: 380,
    tier: 2
  },
  {
    id: "D16",
    name: "Concurrency Control",
    description: "Serializability (conflict and view), precedence graphs, lock-based protocols (2PL, strict 2PL), and deadlock resolution.",
    difficulty: 4,
    learning_objectives: [
      "Build precedence graphs to test conflict serializability",
      "Implement Two-Phase Locking (2PL) and Strict 2PL",
      "Detect and resolve deadlocks with wait-for graphs and timestamps"
    ],
    prerequisites: ["D15"],
    resources: [
      {
        title: "Concurrency Control & Serializability",
        url: "https://en.wikipedia.org/wiki/Concurrency_control",
        summary: "Precedence graphs, lock schedules, and deadlock prevention."
      }
    ],
    x: 380,
    y: 440,
    tier: 3
  },
  {
    id: "D17",
    name: "Indexing (B+ trees)",
    description: "File organization, primary vs secondary indices, clustered indices, and B+ tree index structure and search/insert operations.",
    difficulty: 4,
    learning_objectives: [
      "Compare clustered vs secondary indices",
      "Trace B+ tree search paths and node split logic",
      "Evaluate index selection impact on query execution cost"
    ],
    prerequisites: ["D03", "D08"],
    resources: [
      {
        title: "B+ Tree Indexing Architecture",
        url: "https://en.wikipedia.org/wiki/B%2B_tree",
        summary: "Balanced search tree structure, leaf node linking, and I/O optimization."
      }
    ],
    x: 720,
    y: 290,
    tier: 5
  },
  {
    id: "D18",
    name: "Query Processing & Optimization",
    description: "Query processing stages (parsing, translation, optimization), relational algebra equivalences, and cost-based plan selection.",
    difficulty: 5,
    learning_objectives: [
      "Trace query pipeline: SQL to relational algebra expression trees",
      "Apply heuristic optimization (push selections and projections early)",
      "Estimate query cost using database catalog statistics"
    ],
    prerequisites: ["D07", "D09", "D17"],
    resources: [
      {
        title: "Query Optimization and Plan Selection",
        url: "https://en.wikipedia.org/wiki/Query_optimization",
        summary: "Heuristic and cost-based relational query optimizers."
      }
    ],
    x: 890,
    y: 300,
    tier: 6
  }
];

export const QUESTIONS: Question[] = [
  // D01: DBMS Basics
  {
    id: "Q01A",
    concept: "D01",
    family: "A",
    difficulty: 1,
    prompt: "Which layer of the ANSI-SPARC 3-schema architecture defines the physical storage structure and file organization on disk?",
    options: [
      { id: "a", text: "Conceptual Schema", correct: false, maps_to: "D01", misconception: "Confuses internal storage schema with logical conceptual model" },
      { id: "b", text: "Internal (Physical) Schema", correct: true },
      { id: "c", text: "External Schema", correct: false, maps_to: "D01", misconception: "Confuses end-user view with physical disk layout" },
      { id: "d", text: "Logical View", correct: false, maps_to: "D02", misconception: "Confuses relational tables with storage blocks" }
    ],
    explanation: "The Internal Schema describes physical storage structures, index access paths, and byte layouts on storage devices.",
    validation_status: "reviewed"
  },
  {
    id: "Q01B",
    concept: "D01",
    family: "B",
    difficulty: 1,
    prompt: "If a database administrator alters physical storage from magnetic HDD to NVMe SSD without changing user queries, which principle is demonstrated?",
    options: [
      { id: "a", text: "Logical Data Independence", correct: false, maps_to: "D01", misconception: "Confuses conceptual schema isolation with physical storage changes" },
      { id: "b", text: "Physical Data Independence", correct: true },
      { id: "c", text: "Transaction Atomicity", correct: false, maps_to: "D15", misconception: "Confuses storage independence with ACID transactions" },
      { id: "d", text: "Referential Integrity", correct: false, maps_to: "D04", misconception: "Confuses physical layer with relational constraint enforcement" }
    ],
    explanation: "Physical data independence allows altering physical storage layout without modifying conceptual or external schemas.",
    validation_status: "reviewed"
  },

  // D02: Relational Model
  {
    id: "Q02A",
    concept: "D02",
    family: "A",
    difficulty: 1,
    prompt: "In the formal Relational Model, why are duplicate tuples strictly disallowed in a relation state?",
    options: [
      { id: "a", text: "Because SQL tables cannot store duplicate rows", correct: false, maps_to: "D08", misconception: "Assumes SQL multi-sets dictate formal mathematical relational theory" },
      { id: "b", text: "Because a relation is formally defined as a mathematical set of tuples", correct: true },
      { id: "c", text: "Because foreign keys mandate that every row be referenced", correct: false, maps_to: "D04", misconception: "Conflates set membership with foreign key referential integrity" },
      { id: "d", text: "Because attributes must only contain numeric values", correct: false, maps_to: "D02", misconception: "Misunderstands domain types" }
    ],
    explanation: "In formal relational model theory, a relation is a mathematical set of tuples; by definition, sets contain no duplicate elements.",
    validation_status: "reviewed"
  },
  {
    id: "Q02B",
    concept: "D02",
    family: "B",
    difficulty: 2,
    prompt: "What is the difference between a relation schema and a relation instance (state)?",
    options: [
      { id: "a", text: "Schema is the dynamic set of rows; instance is the fixed column definitions", correct: false, maps_to: "D02", misconception: "Inverts schema (blueprint) and instance (runtime state)" },
      { id: "b", text: "Schema is the structural blueprint (name and attributes); instance is the data populated at a specific point in time", correct: true },
      { id: "c", text: "Schema applies to SQL only; instance applies to NoSQL", correct: false, maps_to: "D01", misconception: "Mistakes basic terminology for cross-paradigm differences" },
      { id: "d", text: "They are completely interchangeable terms", correct: false, maps_to: "D02", misconception: "Fails to distinguish structural definition from temporal data" }
    ],
    explanation: "The schema is the static structural definition (table name and attribute domains), while the instance is the variable data set existing at any given snapshot.",
    validation_status: "reviewed"
  },

  // D03: Keys
  {
    id: "Q03A",
    concept: "D03",
    family: "A",
    difficulty: 2,
    prompt: "Given relation R(A, B, C, D) where {A, B} uniquely identifies every tuple, and no proper subset of {A, B} can identify every tuple. What is {A, B}?",
    options: [
      { id: "a", text: "A superkey but not a candidate key", correct: false, maps_to: "D03", misconception: "Misses the minimality property of candidate keys" },
      { id: "b", text: "A candidate key", correct: true },
      { id: "c", text: "A foreign key referencing table C", correct: false, maps_to: "D03", misconception: "Confuses candidate keys with external table foreign key pointers" },
      { id: "d", text: "A surrogate key generated by the engine", correct: false, maps_to: "D03", misconception: "Confuses natural minimal candidate keys with artificial auto-increment keys" }
    ],
    explanation: "A candidate key is a minimal superkey: it possesses the uniqueness property, and removing any attribute destroys uniqueness.",
    validation_status: "reviewed"
  },
  {
    id: "Q03B",
    concept: "D03",
    family: "B",
    difficulty: 2,
    prompt: "If {A, B} is a candidate key of R(A, B, C, D), which statement regarding superkeys of R is ALWAYS true?",
    options: [
      { id: "a", text: "{A} must be a superkey", correct: false, maps_to: "D03", misconception: "Incorrectly believes a proper subset of a candidate key can be a superkey" },
      { id: "b", text: "{A, B, C} is a superkey of R", correct: true },
      { id: "c", text: "R cannot have any other candidate keys", correct: false, maps_to: "D03", misconception: "Assumes relations can possess only one candidate key" },
      { id: "d", text: "{C, D} must be a candidate key", correct: false, maps_to: "D03", misconception: "Unfounded assumption regarding unverified attributes" }
    ],
    explanation: "Any superset of a candidate key is by definition a superkey, because adding attributes to an already unique identifier retains uniqueness.",
    validation_status: "reviewed"
  },

  // D04: Integrity Constraints
  {
    id: "Q04A",
    concept: "D04",
    family: "A",
    difficulty: 2,
    prompt: "Under referential integrity, what values can a Foreign Key attribute validly contain?",
    options: [
      { id: "a", text: "Only values that currently exist in the referenced primary key, or NULL (unless NOT NULL is specified)", correct: true },
      { id: "b", text: "Any non-null value regardless of the referenced relation", correct: false, maps_to: "D04", misconception: "Fails to grasp referential integrity validation against referenced tables" },
      { id: "c", text: "Must always be identical to the relation's own primary key", correct: false, maps_to: "D03", misconception: "Confuses foreign key references with local primary keys" },
      { id: "d", text: "Foreign keys can never be NULL under any condition", correct: false, maps_to: "D04", misconception: "Confuses Entity Integrity (primary keys) with Referential Integrity (foreign keys)" }
    ],
    explanation: "Referential integrity requires that every foreign key value either matches an existing candidate/primary key value in the referenced relation or is NULL.",
    validation_status: "reviewed"
  },
  {
    id: "Q04B",
    concept: "D04",
    family: "B",
    difficulty: 2,
    prompt: "Table Orders has customer_id referencing Customers(id) with ON DELETE CASCADE. When a row in Customers is deleted, what happens?",
    options: [
      { id: "a", text: "The database rejects the deletion with an error", correct: false, maps_to: "D04", misconception: "Confuses ON DELETE RESTRICT with ON DELETE CASCADE" },
      { id: "b", text: "All rows in Orders with that customer_id are automatically deleted", correct: true },
      { id: "c", text: "customer_id in Orders is set to NULL", correct: false, maps_to: "D04", misconception: "Confuses ON DELETE CASCADE with ON DELETE SET NULL" },
      { id: "d", text: "Orders are duplicated in an archive table", correct: false, maps_to: "D08", misconception: "Imagines implicit backup mechanisms instead of relational action" }
    ],
    explanation: "ON DELETE CASCADE propagates the deletion of the referenced row to all child rows containing matching foreign keys.",
    validation_status: "reviewed"
  },

  // D05: ER Modeling
  {
    id: "Q05A",
    concept: "D05",
    family: "A",
    difficulty: 2,
    prompt: "How is a weak entity set identified in an Entity-Relationship (ER) diagram?",
    options: [
      { id: "a", text: "It has a primary key composed entirely of its own attributes", correct: false, maps_to: "D03", misconception: "Fails to recognize that weak entities lack their own primary key" },
      { id: "b", text: "By combining its partial key (discriminator) with the primary key of its identifying parent entity", correct: true },
      { id: "c", text: "It cannot participate in any relationships", correct: false, maps_to: "D05", misconception: "Misunderstands relationship participation" },
      { id: "d", text: "It is represented with a single dashed circle", correct: false, maps_to: "D05", misconception: "Confuses ER diagram notation conventions" }
    ],
    explanation: "A weak entity does not possess sufficient attributes to form a primary key on its own; it requires its partial key plus the identifying relationship's parent key.",
    validation_status: "reviewed"
  },
  {
    id: "Q05B",
    concept: "D05",
    family: "B",
    difficulty: 2,
    prompt: "In an ER diagram, an employee may manage at most one department, and each department has exactly one manager. What is the cardinality ratio?",
    options: [
      { id: "a", text: "Many-to-Many (M:N)", correct: false, maps_to: "D05", misconception: "Misreads 1:1 constraints as arbitrary many-to-many" },
      { id: "b", text: "One-to-One (1:1)", correct: true },
      { id: "c", text: "One-to-Many (1:N)", correct: false, maps_to: "D05", misconception: "Overlooks the 'at most one' restriction in both directions" },
      { id: "d", text: "Recursive ternary", correct: false, maps_to: "D05", misconception: "Applies advanced relationship terminology incorrectly" }
    ],
    explanation: "Because an employee manages at most 1 department and a department has at most 1 manager, the cardinality ratio is strictly 1:1.",
    validation_status: "reviewed"
  },

  // D06: ER-to-Relational Mapping
  {
    id: "Q06A",
    concept: "D06",
    family: "A",
    difficulty: 3,
    prompt: "When mapping a Many-to-Many (M:N) relationship R between entity sets E1 and E2 into relational tables, what is required?",
    options: [
      { id: "a", text: "Placing the primary key of E1 directly as a foreign key into E2's table", correct: false, maps_to: "D06", misconception: "Applies 1:N foreign key placement to an M:N relationship" },
      { id: "b", text: "Creating a new junction/cross-reference relation containing foreign keys to both E1 and E2", correct: true },
      { id: "c", text: "Merging E1 and E2 into a single wide table", correct: false, maps_to: "D13", misconception: "Violates normalization and causes severe redundancy" },
      { id: "d", text: "Storing a comma-delimited string array of IDs in E1", correct: false, maps_to: "D13", misconception: "Violates First Normal Form (1NF) non-atomic attribute rule" }
    ],
    explanation: "M:N relationships cannot be represented by a single foreign key without repeating rows; they require a separate relationship table (junction table).",
    validation_status: "reviewed"
  },
  {
    id: "Q06B",
    concept: "D06",
    family: "B",
    difficulty: 3,
    prompt: "How is a multivalued attribute (such as an employee having multiple phone numbers) properly mapped to relational tables?",
    options: [
      { id: "a", text: "Create a separate relation with the parent entity's primary key and the attribute value", correct: true },
      { id: "b", text: "Keep all numbers in one attribute separated by commas", correct: false, maps_to: "D13", misconception: "Violates 1NF atomicity requirement" },
      { id: "c", text: "Add 10 static columns: phone1, phone2, ... phone10", correct: false, maps_to: "D06", misconception: "Uses anti-pattern schema design with high null waste" },
      { id: "d", text: "Multivalued attributes are discarded during mapping", correct: false, maps_to: "D05", misconception: "Incorrectly believes data is dropped during schema mapping" }
    ],
    explanation: "A multivalued attribute is mapped to a distinct relation consisting of the parent's primary key (as a foreign key) and the attribute value.",
    validation_status: "reviewed"
  },

  // D07: Relational Algebra
  {
    id: "Q07A",
    concept: "D07",
    family: "A",
    difficulty: 3,
    prompt: "Which relational algebra operation filters rows of a relation based on a specified boolean predicate?",
    options: [
      { id: "a", text: "Projection (π)", correct: false, maps_to: "D07", misconception: "Confuses vertical column projection with horizontal row selection" },
      { id: "b", text: "Selection (σ)", correct: true },
      { id: "c", text: "Cartesian Product (×)", correct: false, maps_to: "D07", misconception: "Confuses tuple pairing with filtering" },
      { id: "d", text: "Natural Join (⨝)", correct: false, maps_to: "D07", misconception: "Confuses multi-relation joins with single relation row filtering" }
    ],
    explanation: "Selection (σ) selects horizontal rows that satisfy a boolean condition, whereas Projection (π) selects vertical columns.",
    validation_status: "reviewed"
  },
  {
    id: "Q07B",
    concept: "D07",
    family: "B",
    difficulty: 3,
    prompt: "If relation R has 4 tuples and relation S has 5 tuples, how many tuples are produced by the Cartesian Product R × S?",
    options: [
      { id: "a", text: "9 tuples", correct: false, maps_to: "D07", misconception: "Adds cardinalities instead of computing the product |R| × |S|" },
      { id: "b", text: "20 tuples", correct: true },
      { id: "c", text: "1 tuple", correct: false, maps_to: "D07", misconception: "Confuses Cartesian product with set intersection" },
      { id: "d", text: "Cannot be determined without a common attribute", correct: false, maps_to: "D09", misconception: "Confuses Cartesian product with natural join requirement" }
    ],
    explanation: "The Cartesian product of relations R and S combines every tuple in R with every tuple in S, producing |R| × |S| = 4 × 5 = 20 tuples.",
    validation_status: "reviewed"
  },

  // D08: SQL Basics
  {
    id: "Q08A",
    concept: "D08",
    family: "A",
    difficulty: 2,
    prompt: "In SQL, what is the result of evaluating the boolean expression `salary > 50000` when `salary` is NULL?",
    options: [
      { id: "a", text: "TRUE", correct: false, maps_to: "D08", misconception: "Incorrectly treats NULL as zero or infinity" },
      { id: "b", text: "FALSE", correct: false, maps_to: "D08", misconception: "Assumes two-valued boolean logic instead of SQL three-valued logic" },
      { id: "c", text: "UNKNOWN", correct: true },
      { id: "d", text: "Syntax Error", correct: false, maps_to: "D08", misconception: "Believes comparing NULL raises an execution exception" }
    ],
    explanation: "SQL uses three-valued logic (TRUE, FALSE, UNKNOWN). Comparing any value against NULL via standard comparison operators yields UNKNOWN.",
    validation_status: "reviewed"
  },
  {
    id: "Q08B",
    concept: "D08",
    family: "B",
    difficulty: 2,
    prompt: "Which clause in a SQL SELECT query is evaluated FIRST during logical query execution?",
    options: [
      { id: "a", text: "SELECT", correct: false, maps_to: "D08", misconception: "Confuses textual query order with internal logical execution order" },
      { id: "b", text: "FROM", correct: true },
      { id: "c", text: "WHERE", correct: false, maps_to: "D08", misconception: "Assumes filter is processed before the source tables are joined" },
      { id: "d", text: "ORDER BY", correct: false, maps_to: "D08", misconception: "Thinks sorting precedes data extraction" }
    ],
    explanation: "In SQL logical execution order, FROM (and JOINs) is evaluated first to assemble the working dataset, followed by WHERE, GROUP BY, HAVING, SELECT, and ORDER BY.",
    validation_status: "reviewed"
  },

  // D09: SQL Joins
  {
    id: "Q09A",
    concept: "D09",
    family: "A",
    difficulty: 3,
    prompt: "Given query: `SELECT * FROM Employees e LEFT OUTER JOIN Departments d ON e.dept_id = d.id;`. Which employees will be included?",
    options: [
      { id: "a", text: "Only employees whose dept_id exists in Departments", correct: false, maps_to: "D09", misconception: "Confuses LEFT OUTER JOIN with INNER JOIN" },
      { id: "b", text: "All employees; those without matching departments will have NULL in department columns", correct: true },
      { id: "c", text: "Only departments with at least one employee", correct: false, maps_to: "D09", misconception: "Confuses LEFT JOIN with RIGHT JOIN" },
      { id: "d", text: "No employees if any dept_id is NULL", correct: false, maps_to: "D08", misconception: "Believes NULL values abort join execution" }
    ],
    explanation: "LEFT OUTER JOIN preserves all rows from the left table (Employees). If no match exists in the right table, columns are padded with NULLs.",
    validation_status: "reviewed"
  },
  {
    id: "Q09B",
    concept: "D09",
    family: "B",
    difficulty: 3,
    prompt: "What happens if you run `SELECT * FROM A, B` without specifying a WHERE condition or JOIN predicate?",
    options: [
      { id: "a", text: "A Natural Join on all matching column names", correct: false, maps_to: "D07", misconception: "Assumes SQL implicitly executes a Natural Join without syntax" },
      { id: "b", text: "A full Cartesian Product of A and B", correct: true },
      { id: "c", text: "A Syntax error is thrown by modern SQL parsers", correct: false, maps_to: "D08", misconception: "Believes comma joins require mandatory WHERE clauses" },
      { id: "d", text: "An empty result set", correct: false, maps_to: "D09", misconception: "Assumes unmatched tables yield zero rows" }
    ],
    explanation: "Listing multiple tables in the FROM clause without a join condition produces a Cartesian product (CROSS JOIN) of all tuples.",
    validation_status: "reviewed"
  },

  // D10: Aggregation and GROUP BY
  {
    id: "Q10A",
    concept: "D10",
    family: "A",
    difficulty: 3,
    prompt: "What is the key difference between the WHERE clause and the HAVING clause in SQL?",
    options: [
      { id: "a", text: "WHERE filters rows before aggregation; HAVING filters aggregated groups", correct: true },
      { id: "b", text: "WHERE only works on numbers; HAVING works on text strings", correct: false, maps_to: "D08", misconception: "Misattributes data-type restrictions to query clauses" },
      { id: "c", text: "HAVING executes before the FROM clause", correct: false, maps_to: "D10", misconception: "Inverts logical execution sequence" },
      { id: "d", text: "They are completely interchangeable in ANSI SQL", correct: false, maps_to: "D10", misconception: "Ignores the grouping boundary distinction between rows and groups" }
    ],
    explanation: "WHERE filters individual tuples before grouping occurs; HAVING filters summarized groups after GROUP BY aggregation.",
    validation_status: "reviewed"
  },
  {
    id: "Q10B",
    concept: "D10",
    family: "B",
    difficulty: 3,
    prompt: "In `SELECT dept, AVG(salary) FROM Employees GROUP BY dept HAVING COUNT(*) > 5;`, which column can NOT be in the SELECT list without an aggregate?",
    options: [
      { id: "a", text: "dept", correct: false, maps_to: "D10", misconception: "Incorrectly believes grouped columns cannot appear in SELECT" },
      { id: "b", text: "employee_name", correct: true },
      { id: "c", text: "AVG(salary)", correct: false, maps_to: "D10", misconception: "Fails to recognize aggregate functions are permitted" },
      { id: "d", text: "Any numeric column", correct: false, maps_to: "D08", misconception: "Assumes datatype rather than grouping rule governs selection" }
    ],
    explanation: "Columns in SELECT that are not in the GROUP BY clause must be wrapped in an aggregate function; otherwise, individual row values are ambiguous within a group.",
    validation_status: "reviewed"
  },

  // D11: Subqueries and Views
  {
    id: "Q11A",
    concept: "D11",
    family: "A",
    difficulty: 4,
    prompt: "What defines a correlated subquery in SQL?",
    options: [
      { id: "a", text: "A subquery that can be executed independently once before the outer query runs", correct: false, maps_to: "D11", misconception: "Describes a non-correlated subquery" },
      { id: "b", text: "A subquery that references attributes from the enclosing outer query, evaluated once per candidate row", correct: true },
      { id: "c", text: "A subquery that only returns scalar integers", correct: false, maps_to: "D11", misconception: "Confuses scalar subqueries with correlated execution" },
      { id: "d", text: "A query created inside a CREATE VIEW statement", correct: false, maps_to: "D11", misconception: "Confuses database views with correlation" }
    ],
    explanation: "A correlated subquery references columns from the outer query, meaning it depends on the outer row context and conceptually executes for each outer row.",
    validation_status: "reviewed"
  },
  {
    id: "Q11B",
    concept: "D11",
    family: "B",
    difficulty: 4,
    prompt: "Why does `WHERE EXISTS (SELECT 1 FROM Orders WHERE customer_id = c.id)` typically perform faster than `IN (SELECT customer_id FROM Orders)` when NULLs are present?",
    options: [
      { id: "a", text: "EXISTS short-circuits upon finding the first matching tuple and is not prone to NULL evaluation traps", correct: true },
      { id: "b", text: "IN forces a full table drop and re-creation", correct: false, maps_to: "D08", misconception: "Bizarre assertion about DDL execution" },
      { id: "c", text: "EXISTS runs on the client application side", correct: false, maps_to: "D01", misconception: "Misplaces database engine execution into client" },
      { id: "d", text: "There is never any performance difference between EXISTS and IN", correct: false, maps_to: "D18", misconception: "Ignores three-valued logic and optimizer execution plans" }
    ],
    explanation: "EXISTS checks only for the existence of at least one matching row (short-circuiting) and boolean truth, avoiding IN's issues with NULL subquery lists.",
    validation_status: "reviewed"
  },

  // D12: Functional Dependencies
  {
    id: "Q12A",
    concept: "D12",
    family: "A",
    difficulty: 3,
    prompt: "Given relation R(A, B, C, D) and functional dependencies F = {A → B, B → C}. What is the attribute closure of A, denoted A+?",
    options: [
      { id: "a", text: "{A, B}", correct: false, maps_to: "D12", misconception: "Fails to apply Armstrong's transitivity axiom (misses B → C)" },
      { id: "b", text: "{A, B, C}", correct: true },
      { id: "c", text: "{A, B, C, D}", correct: false, maps_to: "D03", misconception: "Incorrectly assumes A must be a superkey of all attributes" },
      { id: "d", text: "{A}", correct: false, maps_to: "D12", misconception: "Fails to compute closure beyond reflexivity" }
    ],
    explanation: "Start with {A}. Since A → B, add B ({A, B}). Since B → C, add C ({A, B, C}). D cannot be derived, so A+ = {A, B, C}.",
    validation_status: "reviewed"
  },
  {
    id: "Q12B",
    concept: "D12",
    family: "B",
    difficulty: 3,
    prompt: "According to Armstrong's Axioms, if X → Y holds, which of the following rules guarantees that XZ → YZ must also hold for any attribute set Z?",
    options: [
      { id: "a", text: "Reflexivity Rule", correct: false, maps_to: "D12", misconception: "Confuses reflexivity (Y ⊆ X ⇒ X → Y) with augmentation" },
      { id: "b", text: "Augmentation Rule", correct: true },
      { id: "c", text: "Transitivity Rule", correct: false, maps_to: "D12", misconception: "Confuses transitivity (X → Y, Y → Z ⇒ X → Z) with augmentation" },
      { id: "d", text: "Decomposition Rule", correct: false, maps_to: "D12", misconception: "Confuses splitting right-hand attributes with augmenting both sides" }
    ],
    explanation: "The Augmentation Rule states that if X → Y holds, then adding attribute set Z to both sides (XZ → YZ) is valid.",
    validation_status: "reviewed"
  },

  // D13: Normalization (1NF to 3NF) - Core Demo Concept!
  {
    id: "Q13A",
    concept: "D13",
    family: "A",
    difficulty: 3,
    prompt: "Relation R(A, B, C) has functional dependencies: A → B, B → C. The candidate key is A. Which normal form is R in?",
    options: [
      { id: "a", text: "3NF", correct: false, maps_to: "D13", misconception: "Ignores transitive dependency B → C where non-key determines non-key" },
      { id: "b", text: "2NF but not 3NF", correct: true },
      { id: "c", text: "1NF only", correct: false, maps_to: "D12", misconception: "Cannot compute FDs or confuses dependency direction" },
      { id: "d", text: "BCNF", correct: false, maps_to: "D03", misconception: "Cannot identify candidate keys and determinants from FDs" }
    ],
    explanation: "A is the key, so all non-prime attributes (B, C) depend on the whole key (2NF holds). But B → C represents a transitive dependency (B is not a superkey, C is not prime), violating 3NF.",
    validation_status: "reviewed"
  },
  {
    id: "Q13B",
    concept: "D13",
    family: "B",
    difficulty: 4,
    prompt: "Relation R(EmpID, DeptID, DeptName) has primary key (EmpID, DeptID). Given DeptID → DeptName, why does this violate 2NF?",
    options: [
      { id: "a", text: "Because DeptName is multi-valued", correct: false, maps_to: "D13", misconception: "Confuses 1NF non-atomic repeating groups with 2NF partial dependencies" },
      { id: "b", text: "DeptName depends on a proper subset (DeptID) of the candidate key (EmpID, DeptID)", correct: true },
      { id: "c", text: "Because EmpID is not an integer", correct: false, maps_to: "D04", misconception: "Attributes relational normal forms to physical datatypes" },
      { id: "d", text: "It does not violate 2NF, it only violates BCNF", correct: false, maps_to: "D14", misconception: "Fails to detect partial dependency on part of composite key" }
    ],
    explanation: "Second Normal Form (2NF) requires that no non-prime attribute is partially dependent on any candidate key. DeptName depends on DeptID alone.",
    validation_status: "reviewed"
  },

  // D14: BCNF and Decomposition
  {
    id: "Q14A",
    concept: "D14",
    family: "A",
    difficulty: 4,
    prompt: "Under what condition is a relational schema R in Boyce-Codd Normal Form (BCNF)?",
    options: [
      { id: "a", text: "For every non-trivial functional dependency X → Y, X must be a superkey of R", correct: true },
      { id: "b", text: "For every functional dependency X → Y, Y must be a prime attribute", correct: false, maps_to: "D13", misconception: "Describes the relaxed condition of 3NF, not the strict BCNF condition" },
      { id: "c", text: "Only when every table contains at most 2 columns", correct: false, maps_to: "D14", misconception: "Confuses 6NF binary decomposition with BCNF" },
      { id: "d", text: "When all foreign keys are disabled", correct: false, maps_to: "D04", misconception: "Irrelevant statement about constraints" }
    ],
    explanation: "BCNF requires that for every non-trivial functional dependency X → Y, the determinant X must be a superkey of R.",
    validation_status: "reviewed"
  },
  {
    id: "Q14B",
    concept: "D14",
    family: "B",
    difficulty: 4,
    prompt: "What is a known disadvantage of decomposing a relation into BCNF compared to 3NF?",
    options: [
      { id: "a", text: "BCNF decompositions are never lossless", correct: false, maps_to: "D14", misconception: "False: BCNF decompositions can always guarantee lossless join" },
      { id: "b", text: "Some functional dependencies might not be preserved across the decomposed tables", correct: true },
      { id: "c", text: "It causes severe update anomalies", correct: false, maps_to: "D13", misconception: "Inverts normalization goals: BCNF eliminates anomalies" },
      { id: "d", text: "SQL cannot query decomposed tables", correct: false, maps_to: "D09", misconception: "Ignores that SQL joins reconstruct decomposed relations" }
    ],
    explanation: "While 3NF guarantees both lossless join and dependency preservation, BCNF guarantees lossless join but may not always preserve all functional dependencies.",
    validation_status: "reviewed"
  },

  // D15: Transactions and ACID
  {
    id: "Q15A",
    concept: "D15",
    family: "A",
    difficulty: 3,
    prompt: "If a database crashes during a bank transfer after debiting Account A but before crediting Account B, which ACID property ensures Account A is refunded upon recovery?",
    options: [
      { id: "a", text: "Isolation", correct: false, maps_to: "D16", misconception: "Confuses concurrent transaction visibility with all-or-nothing execution" },
      { id: "b", text: "Atomicity", correct: true },
      { id: "c", text: "Durability", correct: false, maps_to: "D15", misconception: "Confuses persisting committed data with rolling back uncommitted work" },
      { id: "d", text: "Consistency", correct: false, maps_to: "D04", misconception: "Confuses overall semantic invariants with atomic rollback mechanics" }
    ],
    explanation: "Atomicity ('all or nothing') ensures that if a transaction cannot complete entirely, any intermediate modifications are rolled back.",
    validation_status: "reviewed"
  },
  {
    id: "Q15B",
    concept: "D15",
    family: "B",
    difficulty: 3,
    prompt: "Which concurrency anomaly occurs when Transaction T1 reads modified data from Transaction T2 that is subsequently rolled back?",
    options: [
      { id: "a", text: "Non-repeatable Read", correct: false, maps_to: "D15", misconception: "Confuses rereading committed updates with reading uncommitted dirty data" },
      { id: "b", text: "Dirty Read", correct: true },
      { id: "c", text: "Phantom Read", correct: false, maps_to: "D15", misconception: "Confuses new row insertions satisfying a range with uncommitted reads" },
      { id: "d", text: "Lost Update", correct: false, maps_to: "D16", misconception: "Confuses overwriting concurrent writes with uncommitted read rollback" }
    ],
    explanation: "A Dirty Read occurs when a transaction reads uncommitted changes made by another concurrent transaction that later aborts.",
    validation_status: "reviewed"
  },

  // D16: Concurrency Control
  {
    id: "Q16A",
    concept: "D16",
    family: "A",
    difficulty: 4,
    prompt: "How can one determine whether a concurrent schedule S of transactions is Conflict Serializable?",
    options: [
      { id: "a", text: "Check if the precedence (serialization) graph of S contains no cycles", correct: true },
      { id: "b", text: "Ensure all transactions are executed strictly serially one after another", correct: false, maps_to: "D16", misconception: "Demands literal serial execution rather than serializable equivalence" },
      { id: "c", text: "Verify that all transactions only perform read operations", correct: false, maps_to: "D16", misconception: "Trivializes concurrency by eliminating all writes" },
      { id: "d", text: "Count the number of locks acquired", correct: false, maps_to: "D16", misconception: "Confuses lock counts with graph topological acyclicity" }
    ],
    explanation: "A schedule is conflict serializable if and only if its precedence (conflict) graph contains no directed cycles.",
    validation_status: "reviewed"
  },
  {
    id: "Q16B",
    concept: "D16",
    family: "B",
    difficulty: 4,
    prompt: "In the Two-Phase Locking (2PL) protocol, what is the fundamental rule governing lock acquisition and release?",
    options: [
      { id: "a", text: "Transactions may acquire new locks at any time", correct: false, maps_to: "D16", misconception: "Violates the shrinking phase constraint of 2PL" },
      { id: "b", text: "Once a transaction releases any lock (shrinking phase), it can never obtain any new locks", correct: true },
      { id: "c", text: "Only shared locks are allowed", correct: false, maps_to: "D16", misconception: "Ignores exclusive write locks" },
      { id: "d", text: "All locks must be released before the transaction writes any data", correct: false, maps_to: "D15", misconception: "Absurd lock release before writing leads to immediate inconsistency" }
    ],
    explanation: "In 2PL, a transaction has a growing phase (only acquiring locks) and a shrinking phase (only releasing locks). Once a lock is released, no new locks can be acquired.",
    validation_status: "reviewed"
  },

  // D17: Indexing (B+ trees)
  {
    id: "Q17A",
    concept: "D17",
    family: "A",
    difficulty: 4,
    prompt: "Why are B+ trees preferred over standard binary search trees for disk-based relational database indexes?",
    options: [
      { id: "a", text: "Because high branching factor (fan-out) minimizes disk I/O operations and leaf nodes are linked for range scans", correct: true },
      { id: "b", text: "Because binary trees take zero disk space", correct: false, maps_to: "D17", misconception: "Unfounded assertion regarding binary tree storage" },
      { id: "c", text: "Because B+ trees only store integers and cannot index strings", correct: false, maps_to: "D17", misconception: "Misunderstands generic B+ tree key types" },
      { id: "d", text: "B+ trees eliminate the need for primary keys", correct: false, maps_to: "D03", misconception: "Confuses physical access paths with logical keys" }
    ],
    explanation: "B+ trees have a wide branching factor (high fan-out), keeping tree depth small (typically 3-4 levels) which dramatically minimizes expensive disk block reads.",
    validation_status: "reviewed"
  },
  {
    id: "Q17B",
    concept: "D17",
    family: "B",
    difficulty: 4,
    prompt: "What distinguishes a Clustered Index from a Non-Clustered (Secondary) Index?",
    options: [
      { id: "a", text: "A clustered index dictates the physical sorting order of the data rows on disk (at most one per table)", correct: true },
      { id: "b", text: "A clustered index can exist multiple times on the same table", correct: false, maps_to: "D17", misconception: "Fails to grasp that data rows can only have one physical sort order" },
      { id: "c", text: "Non-clustered indexes contain actual data rows in their leaf nodes", correct: false, maps_to: "D17", misconception: "Inverts clustered vs non-clustered leaf node storage" },
      { id: "d", text: "Clustered indexes are stored in RAM only", correct: false, maps_to: "D01", misconception: "Confuses on-disk indexes with in-memory caches" }
    ],
    explanation: "A table can have only one clustered index because the data rows themselves are physically stored in the leaf pages ordered by the cluster key.",
    validation_status: "reviewed"
  },

  // D18: Query Processing and Optimization
  {
    id: "Q18A",
    concept: "D18",
    family: "A",
    difficulty: 5,
    prompt: "In heuristic relational query optimization, why is the 'Push Down Selection' rule universally applied early?",
    options: [
      { id: "a", text: "It reduces the cardinality (number of tuples) before expensive operations like Joins and Cartesian Products", correct: true },
      { id: "b", text: "It converts SQL queries into procedural Python code", correct: false, maps_to: "D01", misconception: "Confuses algebraic optimization with language translation" },
      { id: "c", text: "It sorts the output in ascending order", correct: false, maps_to: "D08", misconception: "Confuses selection predicates with ORDER BY" },
      { id: "d", text: "It deletes rows permanently from the underlying table", correct: false, maps_to: "D08", misconception: "Confuses query filtering with DELETE DML statements" }
    ],
    explanation: "Pushing selections down to the leaf relations filters out unnecessary rows immediately, reducing intermediate table sizes and drastically lowering join computational costs.",
    validation_status: "reviewed"
  },
  {
    id: "Q18B",
    concept: "D18",
    family: "B",
    difficulty: 5,
    prompt: "How does a cost-based query optimizer choose between a Full Table Scan and an Index Scan when executing a WHERE query?",
    options: [
      { id: "a", text: "It always chooses the index scan regardless of table size or selectivity", correct: false, maps_to: "D18", misconception: "Fails to recognize when table scans beat random I/O index lookups" },
      { id: "b", text: "It uses catalog statistics (selectivity, clustering, page counts) to estimate disk I/O and CPU cost for each candidate plan", correct: true },
      { id: "c", text: "It executes all plans simultaneously in production and takes the fastest one", correct: false, maps_to: "D18", misconception: "Absurd cost-doubling execution approach" },
      { id: "d", text: "It randomly selects between them to balance server load", correct: false, maps_to: "D18", misconception: "Misunderstands deterministic cost modeling" }
    ],
    explanation: "A cost-based optimizer uses catalog metadata (row counts, selectivity, page block counts) to calculate estimated I/O and CPU cycles, choosing the lowest-cost execution plan.",
    validation_status: "reviewed"
  }
];

// Seed scenario responses (SRS Section 11.1)
export const DEMO_RESPONSES_HISTORY: ResponseRecord[] = [
  {
    id: "R01",
    question_id: "Q08A",
    concept_id: "D08",
    option_id: "c",
    correct: true,
    confidence: "high",
    response_ms: 1250,
    evidence_weight: 1.0,
    timestamp: "10:14:02"
  },
  {
    id: "R02",
    question_id: "Q07A",
    concept_id: "D07",
    option_id: "b",
    correct: true,
    confidence: "high",
    response_ms: 2100,
    evidence_weight: 1.0,
    timestamp: "10:15:10"
  },
  {
    id: "R03",
    question_id: "Q13A",
    concept_id: "D13",
    option_id: "a",
    correct: false,
    confidence: "high", // High confidence wrong! Evidence weight 1.2
    response_ms: 4500,
    evidence_weight: 1.2,
    distractor_mapped_to: "D13",
    misconception: "Ignores transitive dependency B → C where non-key determines non-key",
    timestamp: "10:16:32"
  },
  {
    id: "R04",
    question_id: "Q12A",
    concept_id: "D12",
    option_id: "a",
    correct: false,
    confidence: "high", // High confidence wrong on D12 targeted question!
    response_ms: 5100,
    evidence_weight: 1.2,
    distractor_mapped_to: "D12",
    misconception: "Fails to apply Armstrong's transitivity axiom (misses B → C)",
    timestamp: "10:17:48"
  },
  {
    id: "R05",
    question_id: "Q12B",
    concept_id: "D12",
    option_id: "c",
    correct: false,
    confidence: "medium", // Second wrong answer on D12 from different question -> Confirms Gap!
    response_ms: 3800,
    evidence_weight: 1.0,
    distractor_mapped_to: "D12",
    misconception: "Confuses transitivity with augmentation",
    timestamp: "10:19:12"
  }
];

export const INITIAL_DIAGNOSTIC_MASTERY: Record<string, StudentMastery> = {
  "D01": { concept_id: "D01", p: 0.85, n_direct: 2, n_indirect: 0, status: "mastered", uncertainty: 0.3 },
  "D02": { concept_id: "D02", p: 0.82, n_direct: 2, n_indirect: 1, status: "mastered", uncertainty: 0.36 },
  "D03": { concept_id: "D03", p: 0.62, n_direct: 1, n_indirect: 2, status: "suspected", uncertainty: 0.76, blocker_score: 0.38 },
  "D04": { concept_id: "D04", p: 0.50, n_direct: 0, n_indirect: 0, status: "insufficient", uncertainty: 1.0 },
  "D05": { concept_id: "D05", p: 0.75, n_direct: 2, n_indirect: 0, status: "mastered", uncertainty: 0.5 },
  "D06": { concept_id: "D06", p: 0.50, n_direct: 0, n_indirect: 0, status: "insufficient", uncertainty: 1.0 },
  "D07": { concept_id: "D07", p: 0.88, n_direct: 2, n_indirect: 0, status: "mastered", uncertainty: 0.24 },
  "D08": { concept_id: "D08", p: 0.90, n_direct: 2, n_indirect: 0, status: "mastered", uncertainty: 0.20 },
  "D09": { concept_id: "D09", p: 0.50, n_direct: 0, n_indirect: 0, status: "insufficient", uncertainty: 1.0 },
  "D10": { concept_id: "D10", p: 0.50, n_direct: 0, n_indirect: 0, status: "insufficient", uncertainty: 1.0 },
  "D11": { concept_id: "D11", p: 0.50, n_direct: 0, n_indirect: 0, status: "insufficient", uncertainty: 1.0 },
  "D12": { concept_id: "D12", p: 0.18, n_direct: 2, n_indirect: 1, status: "confirmed", uncertainty: 0.36, blocker_score: 0.65 },
  "D13": { concept_id: "D13", p: 0.22, n_direct: 1, n_indirect: 0, status: "suspected", uncertainty: 0.44, blocker_score: 0.55 },
  "D14": { concept_id: "D14", p: 0.50, n_direct: 0, n_indirect: 1, status: "insufficient", uncertainty: 1.0 },
  "D15": { concept_id: "D15", p: 0.78, n_direct: 2, n_indirect: 0, status: "mastered", uncertainty: 0.44 },
  "D16": { concept_id: "D16", p: 0.50, n_direct: 0, n_indirect: 0, status: "insufficient", uncertainty: 1.0 },
  "D17": { concept_id: "D17", p: 0.50, n_direct: 0, n_indirect: 0, status: "insufficient", uncertainty: 1.0 },
  "D18": { concept_id: "D18", p: 0.50, n_direct: 0, n_indirect: 0, status: "insufficient", uncertainty: 1.0 }
};

export const POST_RETEST_MASTERY: Record<string, StudentMastery> = {
  ...INITIAL_DIAGNOSTIC_MASTERY,
  "D12": { concept_id: "D12", p: 0.88, n_direct: 3, n_indirect: 1, status: "mastered", uncertainty: 0.24, blocker_score: 0.09 },
  "D13": { concept_id: "D13", p: 0.84, n_direct: 2, n_indirect: 0, status: "mastered", uncertainty: 0.32, blocker_score: 0.11 }
};

export const MOCK_LEARNING_PATH: LearningPathItem[] = [
  {
    id: "PATH-1",
    position: 1,
    concept_id: "D12",
    concept_name: "Functional Dependencies",
    rationale: "Identified as Root Gap: Direct prerequisite of Normalization (D13). Failed targeted diagnostic items Q12A and Q12B with high confidence.",
    completed: false,
    estimated_mins: 8,
    key_takeaways: [
      "X → Y holds if whenever two tuples agree on attributes X, they must strictly agree on Y.",
      "Armstrong's Reflexivity: If Y ⊆ X, then X → Y.",
      "Armstrong's Augmentation: If X → Y, then XZ → YZ.",
      "Armstrong's Transitivity: If X → Y and Y → Z, then X → Z.",
      "Attribute Closure (X+) collects all attributes functionally determined by X."
    ],
    practice_prompt: "Given R(A,B,C,D,E) with FDs: A → B, BC → D, D → E. Compute closure of {A, C}.",
    practice_solution: "{A, C}+ = {A, B, C, D, E}. Because A → B yields B ({A, B, C}), then BC → D yields D, then D → E yields E. Thus {A, C} is a candidate key!"
  },
  {
    id: "PATH-2",
    position: 2,
    concept_id: "D13",
    concept_name: "Normalization (1NF to 3NF)",
    rationale: "Target Concept: Re-learn Normalization now that Functional Dependencies foundation is fortified.",
    completed: false,
    estimated_mins: 10,
    key_takeaways: [
      "1NF: Atomic domain values, no repeating groups or composite nested attributes.",
      "2NF: Relation is in 1NF and no non-prime attribute is partially dependent on any candidate key.",
      "3NF: Relation is in 2NF and no non-prime attribute is transitively dependent on any candidate key (or for every X → A, X is a superkey or A is prime).",
      "Decomposition preserves data without loss (lossless join)."
    ],
    practice_prompt: "Given R(CourseID, Instructor, Office) with CourseID → Instructor, Instructor → Office. Candidate key is CourseID. What normal form is this and how to fix it?",
    practice_solution: "Violates 3NF due to transitive dependency Instructor → Office. Decompose into R1(CourseID, Instructor) and R2(Instructor, Office) to achieve 3NF with no anomalies!"
  }
];

export const TEACHER_COHORT_HEATMAP = [
  { concept_id: "D01", name: "DBMS Basics", confirmed_gaps: 0, suspected_gaps: 2, mastered: 24, insufficient: 2, gap_rate: 7 },
  { concept_id: "D02", name: "Relational Model", confirmed_gaps: 1, suspected_gaps: 3, mastered: 22, insufficient: 2, gap_rate: 14 },
  { concept_id: "D03", name: "Keys", confirmed_gaps: 5, suspected_gaps: 7, mastered: 14, insufficient: 2, gap_rate: 43 },
  { concept_id: "D04", name: "Integrity Constraints", confirmed_gaps: 2, suspected_gaps: 4, mastered: 18, insufficient: 4, gap_rate: 21 },
  { concept_id: "D05", name: "ER Modeling", confirmed_gaps: 1, suspected_gaps: 2, mastered: 23, insufficient: 2, gap_rate: 11 },
  { concept_id: "D06", name: "ER-to-Relational Mapping", confirmed_gaps: 4, suspected_gaps: 6, mastered: 15, insufficient: 3, gap_rate: 36 },
  { concept_id: "D07", name: "Relational Algebra", confirmed_gaps: 3, suspected_gaps: 5, mastered: 18, insufficient: 2, gap_rate: 29 },
  { concept_id: "D08", name: "SQL Basics", confirmed_gaps: 1, suspected_gaps: 2, mastered: 25, insufficient: 0, gap_rate: 11 },
  { concept_id: "D09", name: "SQL Joins", confirmed_gaps: 4, suspected_gaps: 6, mastered: 16, insufficient: 2, gap_rate: 36 },
  { concept_id: "D10", name: "Aggregation & GROUP BY", confirmed_gaps: 2, suspected_gaps: 5, mastered: 19, insufficient: 2, gap_rate: 25 },
  { concept_id: "D11", name: "Subqueries & Views", confirmed_gaps: 6, suspected_gaps: 8, mastered: 11, insufficient: 3, gap_rate: 50 },
  { concept_id: "D12", name: "Functional Dependencies", confirmed_gaps: 11, suspected_gaps: 7, mastered: 8, insufficient: 2, gap_rate: 64 }, // High blocker!
  { concept_id: "D13", name: "Normalization (1NF-3NF)", confirmed_gaps: 9, suspected_gaps: 8, mastered: 9, insufficient: 2, gap_rate: 61 },
  { concept_id: "D14", name: "BCNF & Decomposition", confirmed_gaps: 8, suspected_gaps: 6, mastered: 10, insufficient: 4, gap_rate: 50 },
  { concept_id: "D15", name: "Transactions & ACID", confirmed_gaps: 2, suspected_gaps: 4, mastered: 20, insufficient: 2, gap_rate: 21 },
  { concept_id: "D16", name: "Concurrency Control", confirmed_gaps: 7, suspected_gaps: 6, mastered: 12, insufficient: 3, gap_rate: 46 },
  { concept_id: "D17", name: "Indexing (B+ trees)", confirmed_gaps: 6, suspected_gaps: 7, mastered: 12, insufficient: 3, gap_rate: 46 },
  { concept_id: "D18", name: "Query Optimization", confirmed_gaps: 8, suspected_gaps: 9, mastered: 8, insufficient: 3, gap_rate: 61 }
];

export const SIMULATION_BENCHMARK = [
  {
    strategy: "Baseline A: Fixed Curriculum Order",
    avg_questions_to_diagnose: 11.4,
    diagnostic_accuracy_pct: 54,
    time_efficiency_mins: 28.5,
    root_gap_discovery_rate: 48,
    color: "#94a3b8"
  },
  {
    strategy: "Baseline B: Lowest-Topic-First",
    avg_questions_to_diagnose: 8.7,
    diagnostic_accuracy_pct: 68,
    time_efficiency_mins: 22.0,
    root_gap_discovery_rate: 65,
    color: "#f59e0b"
  },
  {
    strategy: "MIND MESH: Prerequisite DAG Diagnosis",
    avg_questions_to_diagnose: 4.8,
    diagnostic_accuracy_pct: 94,
    time_efficiency_mins: 11.2,
    root_gap_discovery_rate: 96,
    color: "#10b981"
  }
];
