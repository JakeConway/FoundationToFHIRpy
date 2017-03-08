import os
import pprint
import copy
from xml.dom import minidom as domParser

def hasNumber(inputString):
    return any(char.isdigit() for char in inputString)

def addFoundationAsPerformer(resource):
    resource['performer'] = [{
        'reference': "Organization/FM",
        'display': "Foundation Medicine"
    }]

def addPatientSubjectReference(resource, patientId, patientName):
    resource['subject'] = {
        'reference': "Patient/" + patientId,
        'display': patientName
    }

class foundationFhirOrganization:
    def __init__(self):
        self.organizationResource = {
                'resourceType': "Organization",
                'text': {
                    'status': "generated",
                    'div': ""
                }
            }
        self.resourceType = "Organization"

    def getOrganizationName(self):
        return self.organizationResource['name']

def createFoundationMedicineOrganization(FMorganization):
    FMorganization['id'] = "FM"
    FMorganization['identifier'] = [{
        'use': "official",
        'type': {
            'text': "CLIA identification number"
        },
        'system': "https://wwwn.cdc.gov/clia/Resources/LabSearch.aspx",
        'value': "22D2027531"
    }]
    FMorganization['active'] = True
    FMorganization['type'] = {
        'coding': [{
            'system': "http://hl7.org/fhir/ValueSet/organization-type",
            'code': "prov",
            'display': "Genomic healthcare provider"
        }],
        'text': "Genomic healthcare provider"
    }
    FMorganization['name'] = "Foundation Medicine"
    FMorganization['telecom'] = [
        {
            'system': "phone",
            'value': "(+1) 617-418-2200"
        },
        {
            'system': "fax",
            'value': "(+1) 617-418-2290"
        },
        {
            'system': "email",
            'value': "client.services@foundationmedicine.com"
        }
    ]
    FMorganization['address'] = [
        {
            'line': [
                "150 Second Street"
            ],
            'city': "Cambridge",
            'state': "MA",
            'postalCode': "02141",
            'country': "USA"
        }
    ]

def organizationAddIdFromFoundation(organizationResource, foundationTag, DOM):
    id = DOM.getElementsByTagName(foundationTag)[0].childNodes[0].nodeValue
    id = id + 'FM'
    organizationResource['id'] = id

def organizationAddIdentifierFromFoundation(organizationResource, DOM):
    organizationResource['identifier'] = [{
        'value': DOM.getElementsByTagName('MedFacilID')[0].childNodes[0].nodeValue
    }]

def organizationAddNameFromFoundation(organizationResource, DOM):
    organizationResource['name'] = DOM.getElementsByTagName('MedFacilName')[0].childNodes[0].nodeValue

class foundationFhirPractitioner:
    def __init__(self):
        self.practitionerResource = {
            'resourceType': "Practitioner",
            'text': {
                'status': "generated",
                'div': ""
            }
        }
        self.resourceType = "Practitioner"

    def getPractitionerName(self):
        return self.practitionerResource['name'][0]['text']

    def getPractitionerId(self):
        return self.practitionerResource['id']

def practitionerAddIdFromFoundation(practitionerResource, foundationTag, DOM):
    id = DOM.getElementsByTagName(foundationTag)[0].childNodes[0].nodeValue
    id = id + 'FM'
    practitionerResource['id'] = id

def practitionerAddRoleFromFoundation(practitionerResource, foundationTag):
    if (foundationTag == 'OrderingMD'):
        code = '309295000'
        text = 'Physician'
    else:
        code = '81464008'
        text = 'Pathologist'

    practitionerResource['role'] = [{}]
    # TODO: add reference organization for ordering physician (is pathologist assumed to be from same organization?)
    practitionerResource['role'][0]['organization'] = {}
    practitionerResource['role'][0]['code'] = {
        'coding': [{
            'system': "http://snomed.info/sct",
            'code': code
        }],
        'text': text
    }

def practitionerAddNameFromFoundation(practitionerResource, foundationTag, DOM):
    name = DOM.getElementsByTagName(foundationTag)[0].childNodes[0].nodeValue
    name = name.split(', ')
    practitionerResource['name'] = [{}]
    practitionerResource['name'][0]['given'] = name[1].split(' ')
    practitionerResource['name'][0]['family'] = name[0]
    practitionerResource['name'][0]['prefix'] = ['MD']
    practitionerResource['name'][0]['text'] = ' '.join(practitionerResource['name'][0]['given']) + \
                                    ' ' + practitionerResource['name'][0]['family'] + ', ' + \
                                              ', '.join(practitionerResource['name'][0]['prefix'])

class foundationFhirPatient:
    def __init__(self):
        self.patientResource = {
            'resourceType': "Patient",
            'text': {
                'status': "generated",
                'div': ""
            },
            'deceasedBoolean': False
        }
        self.resourceType = "Patient"

    def getPatientFullName(self):
        return self.patientResource['name'][0]['text']

    def getPatientFirstName(self):
        return self.patientResource['name'][0]['given'][0]

    def getPatientLastName(self):
        return self.patientResource['name'][0]['family']

    def getPatientIdentifier(self):
        return self.patientResource['identifier'][0]['value']

    def getPatientId(self):
        return self.patientResource['id']

def patientAddIdFromFoundation(patientResource, DOM):
    id = DOM.getElementsByTagName('MRN')[0].childNodes[0].nodeValue
    id = id + 'FM'
    patientResource['id'] = id

def patientAddIdentifierFromFoundation(patientResource, DOM):
    patientResource['identifier'] = [{}]
    patientResource['identifier'][0]['use'] = "usual"
    patientResource['identifier'][0]['type'] = {
        'coding': [{
            'system': "http://hl7.org/fhir/v2/0203",
            'code': "MR"
        }]
    }
    patientResource['identifier'][0]['value'] = DOM.getElementsByTagName('MRN')[0].childNodes[0].nodeValue
    patientResource['identifier'][0]['assigner'] = {
        'display': DOM.getElementsByTagName('MedFacilName')[0].childNodes[0].nodeValue
    }

def patientAddBirthDateFromFoundation(patientResource, DOM):
    patientResource['birthDate'] = DOM.getElementsByTagName('DOB')[0].childNodes[0].nodeValue

def patientAddGenderFromFoundation(patientResource, DOM):
    patientResource['gender'] = DOM.getElementsByTagName('Gender')[0].childNodes[0].nodeValue.lower()

def patientAddNameFromFoundation(patientResource, DOM):
    patientResource['name'] = [{}]
    patientResource['name'][0]['use'] = "official"
    patientResource['name'][0]['given'] = [DOM.getElementsByTagName('FirstName')[0].childNodes[0].nodeValue]
    patientResource['name'][0]['family'] = DOM.getElementsByTagName('LastName')[0].childNodes[0].nodeValue
    patientResource['name'][0]['text'] = patientResource['name'][0]['given'][0] + " " + patientResource['name'][0]['family']

class foundationFhirDiagnosticReport:
    def __init__(self):
        self.diagnosticReportResource = {
            'resourceType': "DiagnosticReport",
            'text': {
                'status': "generated",
                'div': ""
            },
            'status': "partial",
            'code': {
                'text': "FoundationOne"
            }
        }
        self.observationsInReport = 0
        self.resourceType = "DiagnosticReport"

    def getObservationsInReportCount(self):
        return self.observationsInReport

    def getReportDat(self):
        return self.diagnosticReportResource['effectiveDateTime']

    def getReferencePatientName(self):
        return self.diagnosticReportResource['subject']['display']

    def getNameOfDiagnosticReport(self):
        return self.diagnosticReportResource['code']['text']

    def getConclusionOfDiagnosisReport(self):
        return self.diagnosticReportResource['conclusion']

    def getDiagnosticReportId(self):
        return self.diagnosticReportResource['id']

    def getDiagnosticReportTestPerformed(self):
        return self.diagnosticReportResource['category']['text']

def diagnosticReportAddConclusionFromFoundation(diagnosticReport, DOM):
    summary = DOM.getElementsByTagName('Summaries')[0]
    alterationCount = int(summary.getAttribute('alterationCount'))
    sensitizingCount = int(summary.getAttribute('sensitizingCount'))
    resistiveCount = int(summary.getAttribute('resistiveCount'))
    clinicalTrialCount = int(summary.getAttribute('clinicalTrialCount'))

    applicationSetting = DOM.getElementsByTagName('ApplicationSetting')
    try:
        statement = applicationSetting[0].getElementsByTagName('Value')[0].childNodes[0].nodeValue
    except:
        statement = ""

    diagnosticReport.diagnosticReportResource['conclusion'] = "Patient results: " + str(alterationCount) + \
    " genomic alterations | " + str(sensitizingCount) + " therapies associated with potential clinical benefit | " + \
    str(resistiveCount) + " therapies associated with lack of response | " + str(clinicalTrialCount) + " clinical trials. " + \
    statement
    diagnosticReport.observationsInReport = alterationCount + sensitizingCount + resistiveCount + clinicalTrialCount

def diagnosticReportAddId(diagnosticReportResource, DOM):
    diagnosticReportResource['id'] = DOM.getElementsByTagName('ReportId')[0].childNodes[0].nodeValue + \
    DOM.getElementsByTagName('Version')[0].childNodes[0].nodeValue

def diagnosticReportAddCategoryFromFoundation(diagnosticReportResource, DOM):
    diagnosticReportResource['category'] = {
        'text': DOM.getElementsByTagName('TestType')[0].childNodes[0].nodeValue + " test by Foundation Medicine"
    }

def diagnosticReportAddEffectiveDateTimeFromFoundation(diagnosticReportResource, DOM):
    diagnosticReportResource['effectiveDateTime'] = DOM.getElementsByTagName('CollDate')[0].childNodes[0].nodeValue

def diagnosticReportAddSpecimenReference(diagnosticReportResource, reportId, specimenType):
    diagnosticReportResource['specimen'] = [{
        'reference': "Specimen/" + reportId + "-specimen-1",
        'display': specimenType
    }]

def diagnosticReportReferenceObservations(diagnosticReportResource, observationArr):
    diagnosticReportResource['result'] = []
    l = len(observationArr)
    for i in range(0, l, 1):
        diagnosticReportResource['result'][i] = {
            'reference': "Observation/" + observationArr[i].getObservationId(),
            'display': observationArr[i].getDisplayString()
        }

def diagnosticReportAddContainedArr(diagnosticReportResource, observationArr, specimen):
    diagnosticReportResource['contained'] = []
    l = len(observationArr)
    for i in range(0, l, 1):
        diagnosticReportResource.contained.append(observationArr[i].observationResource)
    diagnosticReportResource.contained.append(specimen.specimenResource)

class foundationFhirObservation:
    def __init__(self):
        self.observationResource = {
            'resourceType': "Observation",
            'text': {
                'status': "generated",
                'div': ""
            },
            'status': "final",
            'category': [{
                'coding': [{
                    'system': "http://hl7.org/fhir/observation-category",
                    'code': "laboratory"
                }],
                'text': "Laboratory result generated by Foundation Medicine"
            }],
            # extension is where all of the genomic fields of the observation will be stored
            'extension': [],
            'performer': [{
                'reference': "Organization/FM",
                'display': "Foundation Medicine"
            }]
        }
        self.resourceType = "Observation"
        self.related = []
        self.display = ""
        self.relatedReportId = ""

    def getReferencePatientName(self):
        return self.observationResource['subject']['display']

    def getObservationId(self):
        return self.observationResource['id']

    def getDisplayString(self):
        return self.display

def initObservations(observationArr, nObservations):
    for i in range(0, nObservations, 1):
        observationArr.append(foundationFhirObservation())

def addReportIdToObservationObj(observationArr, reportId):
    l = len(observationArr)
    for i in range(0, l, 1):
        observationArr[i].relatedReportId = str(reportId)

def addGeneticsInterpretation(observationArr, interpretation, tracker):
    observationArr[tracker['value']].observationResource['extension'].append({
        'url': "http://hl7.org/fhir/StructureDefinition/observation-geneticsInterpretation",
        'valueCodeableConcept': {
            'text': interpretation
        }
    })

def addSequenceVariantTypeFromFoundation(observationArr, alteration, tracker):
    observationArr[tracker['value']].observationResource['extension'].append({
        'url': "http://hl7.org/fhir/StructureDefinition/observation-geneticsDNASequenceVariantType",
        'valueCodeableConcept': {
            'text': alteration
        }
    })

def addAminoAcidChangeFromFoundation(observationArr, alteration, tracker):
    observationArr[tracker['value']].observationResource['extension'].append({
        'url': "http://hl7.org/fhir/StructureDefinition/observation-geneticsAminoAcidChangeName",
        'valueCodeableConcept': {
            'text': alteration
        }
    })

def extractRelatedTherapies(observationArr, geneDOM, gene, tracker, therapiesUsed, therapyDict, geneIndex):
    therapyDOMs = geneDOM.getElementsByTagName('Therapy')
    l = len(therapyDOMs)
    for i in range(0, l, 1):
        therapy = therapyDOMs[i].getElementsByTagName('Name')[0].childNodes[0].nodeValue
        if(therapy in therapiesUsed):
            observationArr[int(geneIndex['value'])].related.append({
                'target': {
                    'reference': "Observation/" + observationArr[therapyDict[therapy]].observationResource['id'],
                    'display': observationArr[therapyDict[therapy]].display
                }
            })
            observationArr[therapyDict[therapy]].related.append({
                'type': "derived-from",
                'target': {
                    'reference': "Observation/" + observationArr[int(geneIndex['value'])].observationResource['id'],
                    'display': "Mutation in " + gene
                }
            })
        else:
            if (therapyDOMs[i].getElementsByTagName('Effect')[0].childNodes[0].nodeValue.lower() == 'sensitizing'):
                display = therapy + " is a therapy associated with potential clinical benefit"
                string = display + ". " + "This therapy was observed as a potential treatment for the patient due to their mutation in " + \
                gene + ". FDA Approved: " + therapyDOMs[i].getElementsByTagName('FDAApproved')[0].childNodes[0].nodeValue
            else:
                display = therapy + " is a therapy associated with a lack of response. "
                string = display + "This therapy was observed as a potential treatment for the patient due to their mutation in " + \
                gene + ". FDA Approved: " + therapyDOMs[i].getElementsByTagName('FDAApproved')[0].childNodes[0].nodeValue

            observationArr[tracker['value']].observationResource['id'] = observationArr[tracker['value']].relatedReportId + "-therapy-" + str((i + 1))
            observationArr[tracker['value']].observationResource['valueString'] = string
            observationArr[tracker['value']].observationResource['comment'] = therapyDOMs[i].getElementsByTagName('Rationale')[0].childNodes[0].nodeValue
            observationArr[tracker['value']].related = [{
                'type': "derived-from",
                'target': {
                    'reference': "Observation/" + observationArr[tracker['value'] - (i + 1)].observationResource['id'],
                    'display': "Mutation in " + gene
                }
            }]
            observationArr[tracker['value'] - (i + 1)].related.append({
                'target': {
                    'reference': "Observation/" + observationArr[tracker['value']].observationResource['id'],
                    'display': display
                }
            })
            observationArr[tracker['value']].display = display
            therapyDict[therapy] = int(tracker['value'])
            therapiesUsed.append(therapy)
            tracker['value'] = tracker['value'] + 1

def extractGenomicInfoInOrder(observationArr, genesDOM, genes, tracker):
    geneDOMs = genesDOM.getElementsByTagName('Gene')
    # keep track of what index the genes are in the observation array to relate them to their suggested clinical trials
    l = len(geneDOMs)
    # same therapy can be applied to > 1 genomic alteration
    therapies = []
    therapyDict = {}
    for i in range(0, l, 1):
        gene = geneDOMs[i].getElementsByTagName('Name')[0].childNodes[0].nodeValue
        genes[gene + '-idNumber'] = str((i + 1))
        genes[gene + '-trackerNumber'] = tracker['value']
        observationArr[tracker['value']].observationResource['id'] = observationArr[tracker['value']].relatedReportId + "-gene-alt-" + str((i + 1))
        observationArr[tracker['value']].observationResource['extension'].append({
            'url': "http://hl7.org/fhir/StructureDefinition/observation-geneticsGene",
            'valueCodeableConcept': {
                'coding': [{
                    'system': "http://www.genenames.org",
                    'display': gene
                }],
                'text': gene
            }
        })
        alterationDOM = geneDOMs[i].getElementsByTagName('Alteration')
        alteration = alterationDOM[0].getElementsByTagName('Name')[0].childNodes[0].nodeValue
        if (hasNumber(alteration) is True):
            addAminoAcidChangeFromFoundation(observationArr, alteration, tracker)
        else:
            addSequenceVariantTypeFromFoundation(observationArr, alteration, tracker)
        addGeneticsInterpretation(observationArr, alterationDOM[0].getElementsByTagName('Interpretation')[0].childNodes[0].nodeValue, tracker)
        observationArr[tracker['value']].observationResource['related'] = []
        observationArr[tracker['value']].display = 'A genomic alteration in ' + gene
        geneIndex = copy.deepcopy(tracker)
        tracker['value'] = tracker['value'] + 1
        # TODO: will also want to pass in the alteration with the gene, instead of just the gene (for display of reference)
        extractRelatedTherapies(observationArr, geneDOMs[i], gene, tracker, therapies, therapyDict, geneIndex)

def extractRelatedClinicalTrials(observationArr, trialsDOM, genes, tracker):
    usedTrials = []
    trialsDict = {}
    trialDOMs = trialsDOM.getElementsByTagName('Trial')
    l = len(trialDOMs)
    for i in range(0, l, 1):
        title = trialDOMs[i].getElementsByTagName('Title')[0].childNodes[0].nodeValue
        relatedGene = trialDOMs[i].getElementsByTagName('Gene')[0].childNodes[0].nodeValue
        if(title in usedTrials):
            observationArr[genes[relatedGene + "-trackerNumber"]].related.append({
                'target': {
                    'reference': "Observation/" + observationArr[trialsDict[title]].observationResource['id'],
                    'display': "A clinical trial suggested as a result of the genomic alteration"
                }
            })
            observationArr[trialsDict[title]].related.append({
                'type': "derived-from",
                'target': {
                    'reference': "Observation/" + observationArr[trialsDict[title]].relatedReportId + "-gene-alt-" +
                                 genes[relatedGene + "-idNumber"],
                    'display': "Mutation in " + relatedGene
                }
            })
        else:
            display = "A clinical trial option suggested as a result of the genomic alterations found in patient"
            string = display + ". The title of the trial is " + title + \
            ". This is a " + trialDOMs[i].getElementsByTagName('StudyPhase')[0].childNodes[0].nodeValue + " clinical trial study. " + \
            "It targets " + trialDOMs[i].getElementsByTagName('Target')[0].childNodes[0].nodeValue + \
            ". The locations this clinical trial is available in are: " + \
            trialDOMs[i].getElementsByTagName('Locations')[0].childNodes[0].nodeValue + ". The NCT ID for this trial is: " + \
            trialDOMs[i].getElementsByTagName('NCTID')[0].childNodes[0].nodeValue
            observationArr[tracker['value']].observationResource['id'] = observationArr[tracker['value']].relatedReportId + "-trial-" + str((i + 1))
            observationArr[tracker['value']].observationResource['valueString'] = string
            observationArr[tracker['value']].observationResource['comment'] = trialDOMs[i].getElementsByTagName('Note')[0].childNodes[0].nodeValue
            observationArr[tracker['value']].related = [{
            'type': "derived-from",
            'target': {
                'reference': "Observation/" + observationArr[tracker['value']].relatedReportId + "-gene-alt-" + genes[relatedGene + "-idNumber"],
                'display': "Mutation in " + relatedGene
            }
            }]
            observationArr[genes[relatedGene + "-trackerNumber"]].related.append({
            'target': {
                'reference': "Observation/" + observationArr[tracker['value']].observationResource['id'],
                'display': "A clinical trial suggested as a result of the genomic alteration"
            }
            })
            observationArr[tracker['value']].display = display
            trialsDict[title] = int(tracker['value'])
            usedTrials.append(title)
            tracker['value'] = tracker['value'] + 1


def observationAddGenomicInfoFromFoundation(observationArr, DOM):
    genesDOM = DOM.getElementsByTagName('Genes')[0]
    trackerObj = {'value': 0}
    genes = {}
    extractGenomicInfoInOrder(observationArr, genesDOM, genes, trackerObj)
    extractRelatedClinicalTrials(observationArr, DOM, genes, trackerObj)

########################################################################################################################
files = [f for f in os.listdir('.') if f.endswith('.xml')]
for f in files:
    DOM = domParser.parse(f)

    FoundationMedicine = foundationFhirOrganization()
    createFoundationMedicineOrganization(FoundationMedicine.organizationResource)

    organization = foundationFhirOrganization()
    organizationAddIdFromFoundation(organization.organizationResource, 'MedFacilID', DOM)
    organizationAddIdentifierFromFoundation(organization.organizationResource, DOM)
    organizationAddNameFromFoundation(organization.organizationResource, DOM)

    orderingPhysician = foundationFhirPractitioner()
    practitionerAddIdFromFoundation(orderingPhysician.practitionerResource, 'OrderingMDId', DOM)
    practitionerAddNameFromFoundation(orderingPhysician.practitionerResource, 'OrderingMD', DOM)
    practitionerAddRoleFromFoundation(orderingPhysician.practitionerResource, 'OrderingMD')

    pathologist = foundationFhirPractitioner()
    practitionerAddNameFromFoundation(pathologist.practitionerResource, 'Pathologist', DOM)
    practitionerAddRoleFromFoundation(pathologist.practitionerResource, 'Pathologist')

    patient = foundationFhirPatient()
    patientAddIdFromFoundation(patient.patientResource, DOM)
    patientAddNameFromFoundation(patient.patientResource, DOM)
    patientAddGenderFromFoundation(patient.patientResource, DOM)
    patientAddBirthDateFromFoundation(patient.patientResource, DOM)
    patientAddIdentifierFromFoundation(patient.patientResource, DOM)

    diagnosticReport = foundationFhirDiagnosticReport()
    # passing in entire diagnosticReport, not just resource, because we record how many observations we have
    diagnosticReportAddConclusionFromFoundation(diagnosticReport, DOM)
    diagnosticReportAddId(diagnosticReport.diagnosticReportResource, DOM)
    diagnosticReportAddCategoryFromFoundation(diagnosticReport.diagnosticReportResource, DOM)
    addPatientSubjectReference(diagnosticReport.diagnosticReportResource, patient.getPatientId(), patient.getPatientFullName())
    diagnosticReportAddEffectiveDateTimeFromFoundation(diagnosticReport.diagnosticReportResource, DOM)

    observationArr = []
    initObservations(observationArr, diagnosticReport.getObservationsInReportCount())
    # add patient id to observation objects since it is used to make the ID of all clinical resources
    addReportIdToObservationObj(observationArr, diagnosticReport.getDiagnosticReportId())
    # we add id to observations when adding genomic information..
    # this is so we can link genomic alterations to therapies and clinical trials
    observationAddGenomicInfoFromFoundation(observationArr, DOM)

    # TODO: Implement the rest of the observation fields
    addPatientSubjectReferenceToObservations(observationArr, patient.getPatientId(), patient.getPatientFullName())
    observationAddEffectiveDateTimeFromFoundation(observationArr, diagnosticReport.getReportDate())
    relatedObservations(observationArr)

    # go back and link all of the observations to the diagnostic report
    diagnosticReportReferenceObservations(diagnosticReport.diagnosticReportResource, observationArr)
    #diagnosticReportAddSpecimenReference(diagnosticReport.diagnosticReportResource, diagnosticReport.getDiagnosticReportId(), specimen.getSpecimenType());
    #diagnosticReportAddContainedArr(diagnosticReport.diagnosticReportResource, observationArr, specimen);