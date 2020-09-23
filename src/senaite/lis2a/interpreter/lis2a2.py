# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIS2A.
#
# SENAITE.LIS2A is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2020 by it's authors.
# Some rights reserved, see README and LICENSE.

CONFIGURATION = {
    "id": "LIS2-A2",
    "extends": "",

    # Criteria used by the interpreter to determine if this definition can be
    # used for the interpretation of a given message
    "selection_criteria": {
        "H.ProcessingID": "P",
        "H.VersionNumber": "LIS2-A2",
    },

    # Criteria used by the interpreter to determine the results to consider
    "result_criteria": {
        "R.ResultStatus": ["", "C", "P", "F", "R", "N"],
    },

    # Mappings between result_data dict fields and message fields. Used by the
    # interpreter for the extraction of result_data dicts from a message. Note
    # a given result_data dict field can map to 1 or more fields from message
    "mappings": {
        "id": [
            "O.SpecimenID",
            "O.InstrumentSpecimenID"
        ],
        "keyword": [
            "R.UniversalTestID",
            "R.UniversalTestID_Name",
            "R.UniversalTestID_ManufacturerCode",
        ],
        "result": "R.Measurement",
        "capture_date": "R.DateTimeStarted",
        "captured_by": [
            "R.OperatorIdentification",
            "R.VerifierIdentification"
        ]
    },

    # Header Record. See LIS2-A2 Section 6
    "H": {
        # The five Latin-1 characters that immediately follow the H (the header
        # ID) define the delimiters to be used throughout the subsequent records
        # of the message. The second character in the header record is the field
        # delimiter, the third character is the repeat delimiter, the fourth
        # character is the component delimiter, and the fifth is the escape
        # character. A field delimiter follows these characters to separate them
        # from subsequent fields. Another way to view this is that the first
        # field contains H and the second field contains the repeat, component,
        # and escape delimiters. Using the example delimiters, the first six
        # characters in the header record would appear as follows: H|\ˆ&|.
        "DelimiterDefinition": 1,
        # A unique number or other ID that uniquely identifies the transmission
        # for use in network systems that have defined acknowledgment protocol
        "MessageControlID": 2,
        # A level security/access password as mutually agreed upon by the sender
        # and receiver
        "AccessPassword": 3,
        # Manufacturer/instrument(s) specific to this line. Using repeat and/or
        # component delimiters, this field may reflect software or firmware
        # revisions, multiple instruments available on the line, etc.
        "SenderName": 4,
        # Address of the sender as specified in LIS2-A2 section 5.6.5
        "SenderStreetAddress_Street": (5, 0),
        "SenderStreetAddress_City": (5, 1),
        "SenderStreetAddress_State": (5, 2),
        "SenderStreetAddress_Zip": (5, 3),
        "SenderStreetAddress_Country": (5, 4),
        # Reserved field is currently unused but reserved for future use
        "ReservedField": 6,
        # Telephone number for voice communication with the sender as specified
        # in LIS2-A2 section 5.6.3
        "SenderTelephoneNumber": 7,
        # Any characteristics of the sender such as, parity, checksums, optional
        # protocols, etc. necessary for establishing a communication link with
        # the sender
        "SenderCharacteristics": 8,
        # The name or other ID of the receiver. Its purpose is verification that
        # the transmission is indeed for the receiver
        "ReceiverID": 9,
        # Any comments or special instructions relating to the subsequent
        # records to be transmitted
        "Comment": 10,
        # The processing ID indicates how this message is to be processed:
        # P: Production. Treat message as active message to be completed
        #    according to standard processing.
        # T: Training. Message is initiated by a trainer and should not have an
        #    effect on the system.
        # D: Debugging: Message is initiated for the purpose of a debugging
        #    program.
        # Q: Quality Control: Message is initiated for the purpose of
        #    transmitting quality control/quality assurance or regulatory data
        "ProcessingID": 11,
        # The version level of the specification, currently LIS2-A2
        "VersionNumber": 12,
        # Date and Time the message was generated using the format specified in
        # LIS2-A2 section 5.6.2
        "DateTime": 13,
    },

    # Patient Record. See LIS2-A2 Section 7
    "P": {
        # For the first patient transmitted, 1 shall be entered, for the second,
        # 2, ... until the last as defined in LIS2-A2 section 5.6.7
        "SequenceNumber": 1,
        # Unique ID assigned and used by the practice to identify the patient
        # and his/her results upon return of the results of testing
        "PracticeAssignedPatientID": 2,
        # Unique processing number assigned to the patient by the laboratory
        "LaboratoryAssignedPatientID": 3,
        # Optionally used for additional, universal, or manufacturer-defined
        # identifiers (such as the social security account no.), as arranged
        # between the transmitter and the receiver. Please note that individuals
        # are not required to provide social security numbers
        "PatientIDNo3": 4,
        # patient’s name shall be presented in the following format: last name,
        # first name, middle name or initial, suffix, and title, and each of
        # these components shall be separated by a component delimiter as
        # described in LIS2-A2 Section 5.6.6
        "ID": (5, 0),
        "Lastname": (5, 1),
        "Firstname": (5, 2),
        "Middlename": (5, 3),
        "Suffix": (5, 4),
        "Title": (5, 5),
        # Optional mother’s maiden name may be required to distinguish between
        # patients with the same birthdate and last name when registry files are
        # very large. This name shall be presented as the mother’s maiden
        # surname, for example, Thompson
        "MothersMaidenName": 6,
        # Shall be presented in the format specified in LIS2-A2 Section 5.6.2
        "BirthDate": 7,
        # Shall be represented by M, F, or U
        "Sex": 8,
        # Patient Race-Ethnic Origin:
        # W: white
        # B: black
        # O: Asian/Pacific Islander
        # NA: Native American/Alaskan Native
        # H: Hispanic
        # Full text names of other ethnic groups may also be entered. Note that
        # multiple answers are permissible, separated by a component delimiter
        "RaceEthnicOrigin": 9,
        # Patient’s mailing address as defined in LIS2-A2 section 5.6.5
        "Address_Street": (10, 0),
        "Address_City": (10, 1),
        "Address_State": (10, 2),
        "Address_Zip": (10, 3),
        "Address_Country": (10, 4),
        # Reserved for future expansion
        "ReservedField": 11,
        # Telephone number for voice communication with the patient as specified
        # in LIS2-A2 section 5.6.3
        "TelephoneNumber": 12,
        # This field shall identify the physician(s) caring for the patient as
        # either names or codes, as agreed upon between the sender and the
        # receiver. Identifiers or names, or both, should be separated by
        # component delimiters as specified in LIS2-A2 Section 5.6.6. Multiple
        # physician names (for example, ordering physician, attending physician,
        # referring physician) shall be separated by repeat delimiters
        "AttendingPhysicianID": 13,
        # Optional text fields for vendor use
        "SpecialField1": 14,
        "SpecialField2": 15,
        # Optional numeric field containing the patient’s height. The default
        # units are centimeters. If measured in terms of another unit, the units
        # should also be transmitted as specified in LIS2-A2 Section 5.6.4.
        "Height": 16,
        # Optional numeric field containing the patient’s weight. The default
        # units are kilograms. If measured in terms of another unit, for
        # example, pounds, the unit name shall also be transmitted as specified
        # in LIS2-A2 Section 5.6.4. Height and weight information is not
        # currently required by all laboratories but is of value in estimating
        # normative values based upon body surface area
        "Weight": 17,
        # This value should be entered either as an ICD-9 code or as free text.
        # If multiple diagnoses are recorded, they shall be separated by repeat
        # delimiters
        "KnownDiagnosis": 18,
        # Used for patient active medications or those suspected, in overdose
        # situations. The generic name shall be used. This field is of use in
        # interpretation of clinical results
        "ActiveMedications": 19,
        # Optional field in free text should be used to indicate such conditions
        # that affect results of testing, such as 16-hour fast (for
        # triglycerides) and no red meat (for hemoccult testing).
        "Diet": 20,
        # Text fields for use by the practice; the optional transmitted text
        # will be returned with the results
        "PracticeFieldNumber1": 21,
        "PracticeFieldNumber2": 22,
        # These values shall be represented as specified in Section 5.1. The
        # discharge date, when included, follows the admission date and is
        # separated from it by a repeat delimiter
        "AdmissionDischargeDates": 23,
        # This value shall be represented by the following minimal list or by
        # extensions agreed upon between the sender and receiver: OP
        # (outpatient), PA (preadmit), IP (inpatient), ER (emergency room)
        "AdmissionStatus": 24,
        # This text value shall reflect the general clinic location or nursing
        # unit, or ward or bed (or both) of the patient in terms agreed upon by
        # the sender and the receiver
        "Location": 25,
        # This field relates to LIS2-A2 Section 7.28. It identifies the class of
        # code or classifiers that are transmitted (e.g. DRGs, or in the future,
        # AVGs [ambulatory visitation groups])
        "NatureAlternativeDiagnosticCode": 26,
        # Alternative diagnostic codes and classifications (e.g., DRG codes) can
        # be included in this field. The nature of the diagnostic code is
        # identified in LIS2-A2 Section 7.27. If multiple codes are included,
        # they should be separated by repeat delimiters. Individual codes can be
        # followed by optional test descriptors (when the latter are present)
        # and must be separated by component delimiters
        "AlternativeDiagnosticCode": 27,
        # Codes or names may be sent as agreed upon between the sender and the
        # receiver. Full names of religions may also be sent as required.
        "Religion": 28,
        # Shall indicate the marital status of the patient as follows:
        # M: married, S: single, D: divorced, W: widowed, A: separated
        "MaritalStatus": 29,
        # Isolation codes indicate precautions that must be applied to protect
        # the patient or staff against infection. The following are suggested
        # codes for common precaution. Multiple precautions can be listed when
        # separated by repeat delimiters. Full text precautions may also be sent
        # ARP (antibiotic resistance precautions), BP (blood and needle
        # precautions), ENP (enteric precautions), etc.
        "IsolationStatus": 30,
        # Patient's primary language. This may be needed when the patient is not
        # fluent in the local language
        "Language": 31,
        # This value indicates the hospital service currently assigned to the
        # patient. Both code and text may be sent when separated by a component
        # delimiter as in LIS2-A2 Section 5.6.6
        "HospitalService": 32,
        # This value indicates the hospital institution currently assigned to
        # the patient. Both code and text may be sent when separated by a
        # component delimiter as in LIS2-A2 Section 5.6.6
        "HospitalInstitution": 33,
        # This value indicates the patient dosage group. For example, A–ADULT,
        # P1–PEDIATRIC (one to six months), P2–PEDIATRIC (six months to three
        # years), etc. Subcomponents of this field may be used to define dosage
        # subgroups
        "DosageCategory": 34,
    },

    # Test Order Record. See LIS2-A2 Section 8
    "O": {
        "SequenceNumber": 1,
        # Unique identifier for the specimen assigned by the information system
        # and returned by the instrument. If the specimen has multiple
        # components further identifying cultures derived from it, these
        # component identifiers will follow the specimen ID and be separated by
        # component delimiters. For example, the specimen ID may contain the
        # specimen number followed by the isolate number, well or cup number
        # (for example, 10435Aˆ01ˆ64).
        "SpecimenID": 2,
        # Unique identifier assigned by the instrument, if different from the
        # information system identifier, and returned with results for use in
        # referring to any results
        "InstrumentSpecimenID": 3,
        # This field shall use universal test ID as described in Section 5.6.1.
        "UniversalTestID": (4, 0),
        # The test or battery name associated with the universal test ID code
        # described above
        "UniversalTestID_Name": (4, 1),
        # In the case where multiple national or international coding schemes
        # exist, this field may be used to determine what coding scheme is
        # employed in the test ID and test ID name fields
        "UniversalTestID_Type": (4, 2),
        # This code may be a number, characters, or a multiple test designator
        # based on manufacturer-defined delimiters (that is, AK.23.34-B).
        # Extensions or qualifiers to this code may be followed by subsequent
        # component fields which must be defined and documented by the
        # manufacturer. For example, this code may represent a three-part
        # identifier such as -Dilution^Diluent^Description
        "UniversalTestID_ManufacturerCode": (4, 3),
        # Test priority codes are as follows: S (stat), A (as soon as possible),
        # R (routine), C (callback), P (preoperative)
        # If more than one priority code applies, they must be separated by
        # repeat delimiters
        "Priority": 5,
        # The date and time the test order should be considered ordered. Usually
        # this will be the date and time the order was recorded. This is the
        # date and time against which the priorities should be considered
        # See section 8.4.7
        "RequestedDate": 6,
        # The actual time the specimen was collected or obtained
        "CollectionDate": 7,
        # End date and time of a timed specimen collection, such as 24-hour
        # urine collection. Specified according to Section 5.6.2
        "CollectionEndTime": 8,
        # Total volume of specimens such as urine or other bulk collections when
        # only aliquot is sent to the instrument. The default unit of measure is
        # milliliters. When units are explicitly represented, they should be
        # separated from the numeric value by a component delimiter, for
        # example, 300ˆg. Should follow the conventions given in Section 5.6.4
        "CollectionVolume": 9,
        # Person and facility which collected the specimen. If there are
        # questions relating to circumstances surrounding the specimen
        # collection, this person will be contacted
        "CollectorID": 10,
        # The action to be taken with respect to the specimens that accompany or
        # precede this request. See Section 8.4.12 for the list of codes to use
        "ActionCode": 11,
        # This field representing either a test or a code shall indicate any
        # special hazard associated with the specimen, for example, a hepatitis
        # patient, suspected anthrax
        "DangerCode": 12,
        # Additional information about the specimen would be provided here and
        # used to report information such as amount of inspired O 2 for blood
        # gases, point in menstrual cycle for cervical pap tests, or other
        # conditions that influence test interpretations
        "RelevantClinicalInformation": 13,
        # Optional field shall contain the actual log-in time recorded in the
        # laboratory. The convention specified in Section 5.6.2 shall be used
        "DateSpecimenReceived": 14,
        # Samples of specimen culture types or sources would be blood, urine,
        # serum, hair, wound, biopsy, sputum, etc.
        "SpecimenDescriptor_Type": (15, 0),
        # Ued specifically to determine the specimen source body site (e.g.,
        # left arm, left hand, right lung)
        "SpecimenDescriptor_Source": (15, 1),
        # Name of the ordering physician in the format outlined in Section 5.6.6
        "OrderingPhysician_ID": (16, 0),
        "OrderingPhysician_Lastname": (16, 1),
        "OrderingPhysician_Firstname": (16, 2),
        "OrderingPhysician_Middlename": (16, 3),
        "OrderingPhysician_Suffix": (16, 4),
        "OrderingPhysician_Title": (16, 5),
        # Telephone number of the requesting physician and will be used in
        # responding to callback orders and for critically abnormal results. Use
        # the format given in Section 5.6.3
        "PhysicianTelephoneNumber": 17,
        # Text sent by the requestor should be returned by the sender along with
        # the response
        "UserFieldNumber1": 18,
        "UserFieldNumber2": 19,
        # Optional field definable for any use by the laboratory
        "LaboratoryFieldNumber1": 20,
        "LaboratoryFieldNumber2": 21,
        # Used to indicate the date and time the results for the order are
        # composed into a report, or into this message or when a status as
        # defined in Sections 8.4.26 or 9.9 is entered or changed. When the
        # information system queries the instrument for untransmitted results,
        # the information in this field may be used to control processing on the
        # communications link. Usually, the ordering service would only want
        # those results for which the reporting date and time is greater than
        # the date and time the inquiring system last received results. Dates
        # and times should be recorded as specified in Section 5.6.2
        "DateTimeResultsReported": 22,
        # Billing charge or accounting reference by this instrument for tests
        # performed
        "InstrumentCharge": 23,
        # This identifier may denote the section of the instrument where the
        # test was performed. In the case where multiple instruments are on a
        # single line or a test was moved from one instrument to another, this
        # field will show which instrument or section of an instrument performed
        # the test
        "InstrumentSectionID": 24,
        # The following codes shall be used:
        # O: order record; user asking that analysis be performed
        # C: correction of previously transmitted results
        # P: preliminary results
        # F: final results
        # X: order cannot be done, order cancelled
        # I: in instrument pending
        # Y: no order on record for this test (in response to query)
        # Z: no record of this patient (in response to query)
        # Q: response to query (this record is a response to a request query)
        "ReportType": 25,
        # Unused but reserved for future expansion
        "ReservedField": 26,
        # The location of specimen collection if different from patient location
        "LocationSpecimenCollection": 27,
        # Used for epidemiological reporting purposes and will show whether the
        # organism identified is the result of a nosocomial (hospital-acquired)
        # infection
        "NosocomialInfectionFlag": 28,
        # In cases where an individual service may apply to the specimen
        # collected, and the service is different from the patient record
        # service, this field may be used to define the specific service
        # responsible for such collection
        "SpecimenService": 29,
        # In cases where the specimen may have been collected in an institution,
        # and the institution is different from the patient record institution,
        # may be used to record the institution of specimen collection
        "SpecimenInstitution": 30
    },

    # Result Record. See LIS2-A2 Section 9
    "R": {
        "SequenceNumber": 1,
        # See Section 5.6.1
        # The first component of the test ID field. This field is currently
        # unused but reserved for the application of a universal test identifier
        # code (LOINC Codes), should one system become available for use at a
        # future time
        "UniversalTestID": (2, 0),
        # The test or battery name associated with the universal test ID code
        # described above
        "UniversalTestID_Name": (2, 1),
        # In the case where multiple national or international coding schemes
        # exist, this field may be used to determine what coding scheme is
        # employed in the test ID and test ID name fields
        "UniversalTestID_Type": (2, 2),
        # This code may be a number, characters, or a multiple test designator
        # based on manufacturer-defined delimiters (that is, AK.23.34-B).
        # Extensions or qualifiers to this code may be followed by subsequent
        # component fields which must be defined and documented by the
        # manufacturer. For example, this code may represent a three-part
        # identifier such as -Dilution^Diluent^Description
        "UniversalTestID_ManufacturerCode": (2, 3),
        # Whether numeric, text, or coded values, the data shall be recorded in
        # ASCII text notation. If the data result contains qualifying elements
        # of equal stature, these should be separated by component delimiters.
        # This applies strictly to results of identical nature (that is, this
        # field may not contain implied subvalues). Use of components within
        # this field should be avoided whenever possible.
        # See Section 9.4 for multiple results
        "Measurement": 3,
        # The abbreviation of units for numeric results shall appear here. ISO
        # standard abbreviations in accordance with ISO 2955 4 should be
        # employed when available (e.g., use mg rather than milligrams). Units
        # can be reported in upper or lower case
        "Units": 4,
        # See Section 9.6
        "ReferenceRanges": 5,
        # Indicate the normalcy status of the result. The characters for
        # representing significant changes either up or down or abnormal values
        # shall be:
        # L: below low normal
        # H: above high normal
        # LL: below panic normal
        # HH: above panic high
        # <: below absolute low, that is off low scale on instrument
        # >: above absolute high, that is off high scale on an instrument
        # N: normal
        # A: abnormal
        # U: significant change up
        # D: significant change down
        # B: better, use when direction not relevant or not defined
        # W: worse, use when direction not relevent or not defined
        "ResultAbnormalFlag": 6,
        # See section 9.8
        "NatureOfAbnormality": 7,
        # Result statuses:
        # C: Correction of previously transmitted results
        # P: Preliminary results
        # F: Final results
        # X: Order cannot be done
        # I: In instrument, results pending
        # S: Partial results
        # M: Result is an MIC level
        # R: Result was previously transmitted
        # N: Record contains necessary information to run a new order
        # Q: Result is a response to an outstanding query
        # V: Operator verified/approved result
        # W: Warning: Validity is questionable
        "ResultStatus": 8,
        # This field shall remain empty if there are no relevant normals or
        # units. Otherwise, it shall be represented as in Section 5.6.2. A
        # change in these data from those recorded in the receiving system's
        # dictionary indicates a need for manual review of the results to detect
        # whether they can be considered the same as preceding ones
        "DateChange": 9,
        # Instrument operator who performed the test
        "OperatorIdentification": (10, 0),
        # Verifier of the test
        "VerifierIdentification": (10, 1),
        # Date and time the instrument started the test
        "DateTimeStarted": 11,
        # Date and time the instrument completed the test
        "DateTimeCompleted": 12,
        # Instrument or section of instrument that performed the measurement
        "InstrumentIdentification": 13,
    },

    # TODO Comment Record. See section 10
    "C": {},

    # TODO Request Information Record. See section 11
    "Q": {},

    # TODO Message Terminator Record. See section 12
    "L": {},

    # TODO Scientific Record. See section 13
    "S":  {},

    # TODO Manufacturer Information Record. See section 14
    "M": {},
}
