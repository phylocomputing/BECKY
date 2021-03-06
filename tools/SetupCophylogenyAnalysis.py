#!/usr/bin/env python
# SetupCophylogenyAnalysis.py

import sys
from optparse import OptionParser
try:
    from lxml import etree as ElementTree
    from lxml.etree import Element, Comment, XMLParser
    ElementTree.set_default_parser(XMLParser(remove_blank_text=True,
                                             remove_comments=True))
except ImportError:
    print >> sys.stderr, '*** lxml unavailable, falling back on standard XML', \
                         'implementation ***'
    from xml.etree import ElementTree
    from xml.etree.ElementTree import Element, Comment

parser = OptionParser()
parser.add_option('-a', '--associations', dest='assoc_filename')
parser.add_option('-i', '--host', dest='HOST_TAXON')
parser.add_option('-j', '--host-xml', dest='HOST_XML')
parser.add_option('-s', '--symbiont', dest='SYMBIONT_TAXON')
parser.add_option('-t', '--symbiont-xml', dest='SYMBIONT_XML')

(options, args) = parser.parse_args()

# XML tags, attributes, etc.
ATTR = 'attr'
BRANCH_RATES = 'branchRates'
CLOCK = 'clock'
COALESCENT_LIKELIHOOD = 'coalescentLikelihood'
COEVOLUTION = 'coevolution'
COEVOLUTION_SIMULATOR = 'coevolutionSimulator'
CONSTANT = 'constant'
COPHYLOGENY = 'cophylogeny'
COPHYLOGENY_LIKELIHOOD = 'cophylogenyLikelihood'
COSPECIATION_OPERATOR = 'cospeciationOperator'
DUPLICATION_RATE = 'duplicationRate'
FALSE = 'false'
FILE_NAME = 'fileName'
GAMMA_PRIOR = 'gammaPrior'
HOST = 'host'
HOST_ATTRIBUTE_NAME = 'hostAttributeName'
HOST_SWITCH_OPERATOR = 'hostSwitchOperator'
HOST_SWITCH_RATE = 'hostSwitchRate'
HOST_TAXON = options.HOST_TAXON
HOST_TREE = 'hostTree'
ID = 'id'
IDREF = 'idref'
LIKELIHOOD = 'likelihood'
LOG = 'log'
LOG_TREE = 'logTree'
LOSS_RATE = 'lossRate'
LOWER = 'lower'
MCMC = 'mcmc'
MODEL = 'model'
NAME = 'name'
NODE_REF = 'nodeRef'
NODE_REF_PROVIDER = 'nodeRefProvider'
OFFSET = 'offset'
OPERATOR_ANALYSIS = 'operatorAnalysis'
OPERATORS = 'operators'
ORIGIN = 'origin'
PARAMETER = 'parameter'
PRIOR = 'prior'
POP_SIZE = 'popSize'
POSTERIOR = 'posterior'
RATE =  'rate'
REPORT = 'report'
SAMPLE_NO_HOST = 'sampleNoHost'
SCALE = 'scale'
SCALE_FACTOR = 'scaleFactor'
SCALE_OPERATOR = 'scaleOperator'
SHAPE = 'shape'
SIMPLE_COPHYLOGENY_MODEL = 'simpleCophylogenyModel'
SIMULATE_NO_HOST = 'simulateNoHost'
SIMULATOR = 'simulator'
SPECIATION_LIKELIHOOD = 'speciationLikelihood'
STATE_TAG_NAME = 'stateTagName'
STRICT_CLOCK_BRANCH_RATES = 'strictClockBranchRates'
SUBSTITUTIONS = 'substitutions'
SYMBIONT_TAXON = options.SYMBIONT_TAXON
SYMBIONT_TREE = 'symbiontTree'
TAG = 'tag'
TAG_NAME = 'tagName'
TAXA = 'taxa'
TAXON = 'taxon'
TRAIT = 'trait'
TREE_MODEL = 'treeModel'
TRUE = 'true'
TUG_OPERATOR = 'tugOperator'
UNIFORM_PRIOR = 'uniformPrior'
UNITS = 'units'
UPPER = 'upper'
VALUE = 'value'
WEIGHT = 'weight'

PREFIXLESS_ELEMENT_TAGS = {TAXON, OPERATORS, MCMC, POSTERIOR, PRIOR, LIKELIHOOD,
                           LOG}
TREE_PRIORS = {COALESCENT_LIKELIHOOD, SPECIATION_LIKELIHOOD}

BEGIN_COPHYLOGENY_MODEL_XML = \
    lambda: Comment(text=' BEGIN COPHYLOGENY MODEL XML ')
END_COPHYLOGENY_MODEL_XML = lambda: Comment(text=' END COPHYLOGENY MODEL XML ')

associations = {}

operators = []
priors = []
file_log = []
host_tree_traits = []
symbiont_tree_traits = []

def parse_associations():
    assoc_file = open(options.assoc_filename, 'r')
    for line in assoc_file:
        symbiont, host = line[:-1].split('\t')
        associations[symbiont] = host
    assoc_file.close()

def create_idref(tag, idref):
    return Element(tag, attrib={IDREF: idref})

def create_nested_element(nest_tag, element):
    ni = Element(nest_tag)
    ni.append(element)
    return ni

def create_nested_idref(nest_tag, element_tag, idref):
    return create_nested_element(nest_tag, create_idref(element_tag, idref))

def create_host_attribute(idref):
    ha = Element(ATTR, attrib={NAME: HOST})
    ha.append(create_idref(TAXON, idref))
    return ha

def create_tree_trait(name, tag, idref):
    tt = Element(TRAIT, attrib={NAME: name, TAG: name})
    tt.append(create_idref(tag, idref))
    return tt

def create_scale_operator(idref, scale_factor='0.75', weight='0.1'):
    so = Element(SCALE_OPERATOR,
                 attrib={SCALE_FACTOR: scale_factor, WEIGHT: weight})
    so.append(create_idref(PARAMETER, idref))
    return so

def create_uniform_prior(idref, lower='0.0', upper='1.0E100'):
    up = Element(UNIFORM_PRIOR, attrib={LOWER: lower, UPPER: upper})
    up.append(create_idref(PARAMETER, idref))
    return up

def create_gamma_prior(idref, shape='3.0', scale='0.5', offset='0.0'):
    gp = Element(GAMMA_PRIOR,
                 attrib={SHAPE: shape, SCALE: scale, OFFSET: offset})
    gp.append(create_idref(PARAMETER, idref))
    return gp

def create_host_switch_operator():
    hso = Element(HOST_SWITCH_OPERATOR,
                  attrib={SAMPLE_NO_HOST: FALSE, WEIGHT: '60'})
    hso.append(create_nested_idref(HOST_TREE, TREE_MODEL,
                                   '.'.join([HOST_TAXON, TREE_MODEL])))
    hso.append(create_nested_idref(SYMBIONT_TREE, TREE_MODEL,
                                   '.'.join([SYMBIONT_TAXON, TREE_MODEL])))
    hso.append(create_idref(COPHYLOGENY_LIKELIHOOD,
                            '.'.join([COPHYLOGENY, LIKELIHOOD])))
    return hso

def create_cospeciation_operator():
    co = Element(COSPECIATION_OPERATOR,
                  attrib={WEIGHT: '3'})
    co.append(create_nested_idref(HOST_TREE, TREE_MODEL,
                                   '.'.join([HOST_TAXON, TREE_MODEL])))
    co.append(create_nested_idref(SYMBIONT_TREE, TREE_MODEL,
                                   '.'.join([SYMBIONT_TAXON, TREE_MODEL])))
    co.append(create_idref(COPHYLOGENY_LIKELIHOOD,
                            '.'.join([COPHYLOGENY, LIKELIHOOD])))
    return co

def create_tug_operator():
    to = Element(TUG_OPERATOR, attrib={WEIGHT: '3'})
    to.append(create_nested_idref(HOST_TREE, TREE_MODEL,
                                   '.'.join([HOST_TAXON, TREE_MODEL])))
    to.append(create_nested_idref(SYMBIONT_TREE, TREE_MODEL,
                                   '.'.join([SYMBIONT_TAXON, TREE_MODEL])))
    to.append(create_idref(COPHYLOGENY_LIKELIHOOD,
                            '.'.join([COPHYLOGENY, LIKELIHOOD])))
    return to

def create_host_switching_wilson_balding():
    hswb = Element(HOST_SWITCHING_WILSON_BALDING, attrib={WEIGHT: '3'})
    hswb.append(create_idref(TREE_MODEL, '.'.join([SYMBIONT, TREE_MODEL])
    hswb.append(create_idref(COPHYLOGENY_LIKELIHOOD, '.'.join([COPHYLOGENY, LIKELIHOOD])))
    return hswb

def create_simple_cophylogeny_model():
    scm = Element(SIMPLE_COPHYLOGENY_MODEL,
                  attrib={ID: '.'.join([COPHYLOGENY, MODEL]),
                           UNITS: SUBSTITUTIONS})
    for event_rate in [DUPLICATION_RATE, HOST_SWITCH_RATE, LOSS_RATE]:
        id = '.'.join([COPHYLOGENY, event_rate])
        scm.append(create_nested_element(event_rate,
                                         Element(PARAMETER,
                                                 attrib={ID: id,
                                                          VALUE: '1.0',
                                                          LOWER: '0.0'})))
        if event_rate is not LOSS_RATE:
            operators.append(create_scale_operator(id))
            priors.append(create_gamma_prior(id))
        file_log.append(create_idref(PARAMETER, id))
    return scm

def create_strict_clock_branch_rates():
    id = '.'.join([COPHYLOGENY, CLOCK, RATE])
    scbr = Element(STRICT_CLOCK_BRANCH_RATES,
                   attrib={ID: '.'.join([COPHYLOGENY, BRANCH_RATES])})
    scbr.append(create_nested_element(RATE, Element(PARAMETER,
                                                    attrib={ID: id,
                                                             VALUE: '1.0',
                                                             LOWER: '0.0'})))
    operators.append(create_scale_operator(id, weight='3'))
    priors.append(create_uniform_prior(id))
    file_log.append(create_idref(PARAMETER, id))
    symbiont_tree_traits.append(create_tree_trait(
                                    '.'.join([COPHYLOGENY, RATE]),
                                     STRICT_CLOCK_BRANCH_RATES,
                                     '.'.join([COPHYLOGENY, BRANCH_RATES])))
    return scbr

def create_coevolution_simulator():
    cs = Element(COEVOLUTION_SIMULATOR, attrib={ID: '.'.join([COPHYLOGENY,
                                                               SIMULATOR]),
                                                 HOST_ATTRIBUTE_NAME: HOST,
                                                 SIMULATE_NO_HOST: FALSE})
    cs.append(create_nested_idref(HOST_TREE, TREE_MODEL,
                                   '.'.join([HOST_TAXON, TREE_MODEL])))
    cs.append(create_nested_idref(SYMBIONT_TREE, TREE_MODEL,
                                   '.'.join([SYMBIONT_TAXON, TREE_MODEL])))
    cs.append(create_idref(COPHYLOGENY_LIKELIHOOD,
                            '.'.join([COPHYLOGENY, LIKELIHOOD])))
    return cs

def create_node_ref_provider():
    id = '.'.join([HOST_TAXON, NODE_REF])
    nrp = Element(NODE_REF_PROVIDER, attrib={ID: id, TAG_NAME: NODE_REF})
    nrp.append(create_idref(TREE_MODEL, '.'.join([HOST_TAXON, TREE_MODEL])))
    host_tree_traits.append(create_tree_trait(NODE_REF, NODE_REF_PROVIDER, id))
    return nrp

def create_cophylogeny_likelihood():
    id = '.'.join([COPHYLOGENY, LIKELIHOOD])
    cl = Element(COPHYLOGENY_LIKELIHOOD, attrib={ID: id,
                                                  STATE_TAG_NAME:
                                                      '.'.join([HOST,
                                                                NODE_REF])})
    cl.append(create_idref(SIMPLE_COPHYLOGENY_MODEL,
                           '.'.join([COPHYLOGENY, MODEL])))
    cl.append(create_nested_idref(HOST_TREE, TREE_MODEL,
                                   '.'.join([HOST_TAXON, TREE_MODEL])))
    cl.append(create_nested_idref(SYMBIONT_TREE, TREE_MODEL,
                                   '.'.join([SYMBIONT_TAXON, TREE_MODEL])))
    cl.append(create_idref(STRICT_CLOCK_BRANCH_RATES,
                           '.'.join([COPHYLOGENY, BRANCH_RATES])))
    origin_id = '.'.join([COPHYLOGENY, SYMBIONT, ORIGIN])
    cl.append(Element(PARAMETER, attrib={ID: origin_id,
                                         VALUE:'100.0'
                                         LOWER:'0.0'})
    file_log.append(create_idref(COPHYLOGENY_LIKELIHOOD, id))
    file_log.append(create_idref(PARAMETER, origin_id)
    operators.append(create_host_switch_operator())
    operators.append(create_cospeciation_operator())
    operators.append(create_tug_operator())
    operators.append(create_host_switching_wilson_balding())
    symbiont_tree_traits.append(create_tree_trait('.'.join([HOST, NODE_REF]),
                                                  COPHYLOGENY_LIKELIHOOD,
                                                  id))
    return cl

def append_id_prefix(element_tree, prefix):
    for element in element_tree.iter():
        if element.tag not in PREFIXLESS_ELEMENT_TAGS:
            if ID in element.keys():
                element.set(ID, prefix + '.' + element.get(ID))
            elif IDREF in element.keys():
                element.set(IDREF, prefix + '.' + element.get(IDREF))

host_xml = options.HOST_XML
symbiont_xml = options.SYMBIONT_XML
host_ET = ElementTree.parse(host_xml)
append_id_prefix(host_ET, HOST_TAXON)
symbiont_ET = ElementTree.parse(symbiont_xml)
append_id_prefix(symbiont_ET, SYMBIONT_TAXON)

parse_associations()
symbiont_taxa = symbiont_ET.find(TAXA)
for taxon in symbiont_taxa.iterfind(TAXON):
    taxon.append(create_host_attribute(associations[taxon.get(ID)]))

host_root = host_ET.getroot()
host_operators = host_ET.find(OPERATORS)
host_mcmc = host_ET.find(MCMC)
host_mcmc.set(OPERATOR_ANALYSIS, COEVOLUTION + '.ops')
host_priors = host_mcmc.find(POSTERIOR).find(PRIOR)
host_likelihoods = host_mcmc.find(POSTERIOR).find(LIKELIHOOD)
host_log = host_mcmc.findall(LOG)[1]
host_tree_logs = list(host_mcmc.iterfind(LOG_TREE))

symbiont_root = symbiont_ET.getroot()
symbiont_operators = symbiont_ET.find(OPERATORS)
symbiont_mcmc = symbiont_ET.find(MCMC)
symbiont_priors = symbiont_mcmc.find(POSTERIOR).find(PRIOR)
symbiont_likelihoods = symbiont_mcmc.find(POSTERIOR).find(LIKELIHOOD)
screen_log, symbiont_log = symbiont_mcmc.findall(LOG)[:2]
symbiont_log.remove(symbiont_log.find(POSTERIOR))
symbiont_log.remove(symbiont_log.find(PRIOR))
symbiont_log.remove(symbiont_log.find(LIKELIHOOD))
symbiont_mcmc.remove(screen_log)
symbiont_tree_logs = list(symbiont_mcmc.iterfind(LOG_TREE))

symbiont_root.remove(symbiont_root.find(REPORT))

for operator in symbiont_operators.iterfind('*'):
    if not (operator.find(PARAMETER) is not None and \
        '.'.join([CONSTANT, POP_SIZE]) in operator.find(PARAMETER).get(IDREF)):
        host_operators.append(operator)
symbiont_root.remove(symbiont_operators)

for prior in symbiont_priors.iterfind('*'):
    if prior.tag not in TREE_PRIORS and not \
        (prior.find(PARAMETER) is not None and \
        '.'.join([CONSTANT, POP_SIZE]) in prior.find(PARAMETER).get(IDREF)):
        host_priors.append(prior)
for likelihood in symbiont_likelihoods.iterfind('*'):
    host_likelihoods.append(likelihood)
symbiont_mcmc.remove(symbiont_mcmc.find(POSTERIOR))
symbiont_mcmc.remove(symbiont_mcmc.find(OPERATORS))

for loggable in symbiont_log.iterfind('*'):
    if loggable.tag not in TREE_PRIORS and not \
        '.'.join([CONSTANT, POP_SIZE]) in loggable.get(IDREF):
        host_log.append(loggable)
symbiont_mcmc.remove(symbiont_log)

for element in symbiont_mcmc.iterfind('*'):
    host_mcmc.append(element)
symbiont_root.remove(symbiont_mcmc)

i = 0
for element in host_root.iterfind('*'):
    if element.tag == OPERATORS: break
    i += 1

for element in symbiont_root.iterfind('*'):
    host_root.insert(i, element)
    i += 1

host_root.insert(i, BEGIN_COPHYLOGENY_MODEL_XML())
i += 1
host_root.insert(i, create_simple_cophylogeny_model())
i += 1
host_root.insert(i, create_strict_clock_branch_rates())
i += 1
host_root.insert(i, create_cophylogeny_likelihood())
i += 1
host_root.insert(i, create_coevolution_simulator())
i += 1
host_root.insert(i, create_node_ref_provider())
i += 1
host_root.insert(i, END_COPHYLOGENY_MODEL_XML())

host_operators.append(BEGIN_COPHYLOGENY_MODEL_XML())
for operator in operators:
    host_operators.append(operator)
host_operators.append(END_COPHYLOGENY_MODEL_XML())

host_priors.append(BEGIN_COPHYLOGENY_MODEL_XML())
for prior in priors:
    host_priors.append(prior)
host_priors.append(END_COPHYLOGENY_MODEL_XML())

host_log.set(FILE_NAME, COEVOLUTION + '.log')
host_log.append(BEGIN_COPHYLOGENY_MODEL_XML())
for parameter in file_log:
    host_log.append(parameter)
host_log.append(END_COPHYLOGENY_MODEL_XML())

host_likelihoods.append(BEGIN_COPHYLOGENY_MODEL_XML())
host_likelihoods.append(create_idref(COPHYLOGENY_LIKELIHOOD,
                                     '.'.join([COPHYLOGENY, LIKELIHOOD])))
host_likelihoods.append(END_COPHYLOGENY_MODEL_XML())

for log in host_tree_logs:
    log.append(BEGIN_COPHYLOGENY_MODEL_XML())
    log.extend(host_tree_traits)
    log.append(END_COPHYLOGENY_MODEL_XML())

for log in symbiont_tree_logs:
    log.append(BEGIN_COPHYLOGENY_MODEL_XML())
    log.extend(symbiont_tree_traits)
    log.append(END_COPHYLOGENY_MODEL_XML())

try:
    host_ET.write(sys.stdout, pretty_print=True)
except TypeError:
    host_ET.write(sys.stdout)
