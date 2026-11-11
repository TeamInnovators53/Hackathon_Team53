-- ==============================================================================
-- KeyBank VRU Schema: Household Relationship Groups & Primacy / Privilege Routing
-- Release: October 2026 Release (feature/oct_rel_26)
-- Team Innovators • Hackathon Team 53
-- ==============================================================================

-- 1. Create Relationship Groups Table (VRU_APP_SCHEMA)
CREATE TABLE VRU_APP_SCHEMA.RELATIONSHIP_GROUPS (
    IP_I NUMBER(12, 0) NOT NULL,
    RLP_GRPS VARCHAR2(10) NOT NULL,
    CUST_TIER VARCHAR2(30) DEFAULT 'PRIVILEGED' NOT NULL,
    APPL_TYPE VARCHAR2(20) DEFAULT 'KEYPRIV' NOT NULL,
    LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT PK_RELATIONSHIP_GROUPS PRIMARY KEY (IP_I)
);

COMMENT ON TABLE VRU_APP_SCHEMA.RELATIONSHIP_GROUPS IS 'Household Relationship Groups (A-H) mapping for Key Privilege and CC Primacy routing';
COMMENT ON COLUMN VRU_APP_SCHEMA.RELATIONSHIP_GROUPS.IP_I IS 'Core Enterprise Customer IPI Number';
COMMENT ON COLUMN VRU_APP_SCHEMA.RELATIONSHIP_GROUPS.RLP_GRPS IS 'Household Relationship Group Code (A, B, C, D, E, F, G, H)';

-- 2. Seed Test Privileged Customers for Hackathon Demo
-- Customer 1: Eleanor Vance (At-Risk of Maintenance Fee, Group D)
INSERT INTO VRU_APP_SCHEMA.RELATIONSHIP_GROUPS (IP_I, RLP_GRPS, CUST_TIER, APPL_TYPE)
VALUES (31379551, 'D', 'PRIVILEGED', 'KEYPRIV');

-- Customer 2: Dr. Julian Sterling (Private Client Ultra-HNW, Group A)
INSERT INTO VRU_APP_SCHEMA.RELATIONSHIP_GROUPS (IP_I, RLP_GRPS, CUST_TIER, APPL_TYPE)
VALUES (4645906, 'A', 'PRIVATE_CLIENT', 'PRIVBANK');

-- Customer 3: Marcus Thorne (Key Privilege with Mortgage Exemption, Group C)
INSERT INTO VRU_APP_SCHEMA.RELATIONSHIP_GROUPS (IP_I, RLP_GRPS, CUST_TIER, APPL_TYPE)
VALUES (19284752, 'C', 'PRIVILEGED', 'KEYPRIV');

-- Customer 4: Sofia Ramirez-Cruz (Bilingual Spanish Privilege, Group B)
INSERT INTO VRU_APP_SCHEMA.RELATIONSHIP_GROUPS (IP_I, RLP_GRPS, CUST_TIER, APPL_TYPE)
VALUES (48291043, 'B', 'PRIVILEGED', 'KEYPRIV');

-- 3. Register Transfer Route Codes (TRCs) in 01-specialMessagingVRUUpdated.sql
-- TRC190: MMCCA_PRIMACY (Primacy Credit Card queue)
-- TRC191: KEY_PRIVATE_CLIENT_TRC (Key Private Client Concierge desk)
-- TRC192: KEYPRIVCCA (Key Privilege Priority queue)
-- TRC193: MMCCA_SPANISH (Spanish VIP Queue safeguarding 20-char EDW limit)
INSERT INTO VRU_APP_SCHEMA.SPECIAL_MESSAGING_TRCS (TRC_CODE, DESCRIPTION, ROUTE_POINT, IS_ACTIVE)
VALUES ('KEY_PRIVATE_CLIENT_TRC', 'Key Private Client Dedicated Wealth Concierge', '5554001', 'Y');

INSERT INTO VRU_APP_SCHEMA.SPECIAL_MESSAGING_TRCS (TRC_CODE, DESCRIPTION, ROUTE_POINT, IS_ACTIVE)
VALUES ('KEYPRIVCCA', 'Key Privilege Priority Telephony Queue', '5554002', 'Y');

INSERT INTO VRU_APP_SCHEMA.SPECIAL_MESSAGING_TRCS (TRC_CODE, DESCRIPTION, ROUTE_POINT, IS_ACTIVE)
VALUES ('MMCCA_PRIMACY', 'Credit Card Primacy Queue (Groups A-H)', '5553001', 'Y');

INSERT INTO VRU_APP_SCHEMA.SPECIAL_MESSAGING_TRCS (TRC_CODE, DESCRIPTION, ROUTE_POINT, IS_ACTIVE)
VALUES ('MMCCA_SPANISH', 'Spanish Bilingual Priority Queue (EDW 20-char limit)', '5553002', 'Y');

COMMIT;
