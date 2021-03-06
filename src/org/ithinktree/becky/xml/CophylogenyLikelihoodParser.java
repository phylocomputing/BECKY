/**
 * CophylogenyLikelihoodParser.java
 * 
 * BECKY - Bayesian Estimation of Coevolutionary KrYteria
 * 
 */

package org.ithinktree.becky.xml;

import org.ithinktree.becky.CophylogenyLikelihood;
import org.ithinktree.becky.CophylogenyModel;

import dr.evolution.tree.MutableTree;
import dr.evolution.tree.Tree;
import dr.evomodel.branchratemodel.BranchRateModel;
import dr.inference.model.Parameter;
import dr.xml.AbstractXMLObjectParser;
import dr.xml.AttributeRule;
import dr.xml.ElementRule;
import dr.xml.XMLObject;
import dr.xml.XMLParseException;
import dr.xml.XMLSyntaxRule;

/**
 * Parser for the CophylogenyLikelihood Class.
 * 
 * @author Arman D. Bilge
 *
 */
public class CophylogenyLikelihoodParser extends AbstractXMLObjectParser {

	public static final String COPHYLOGENY_LIKELIHOOD = "cophylogenyLikelihood";
	public static final String MODEL = "model";
	public static final String HOST_TREE = "hostTree";
	public static final String SYMBIONT_TREE = "symbiontTree";
	public static final String CLOCK_MODEL = "clockModel";
	public static final String RECONSTRUCTION_TAG_NAME = "stateTagName";

	
	@Override
	public String getParserName() {
		return COPHYLOGENY_LIKELIHOOD;
	}


	@Override
	public Object parseXMLObject(XMLObject xo) throws XMLParseException {
		
		final String reconstructionTagName = xo.getStringAttribute(RECONSTRUCTION_TAG_NAME);
				
		final CophylogenyModel cophylogenyModel = (CophylogenyModel) xo.getChild(CophylogenyModel.class);
				
		XMLObject cxo = xo.getChild(HOST_TREE);
		final Tree hostTree = (Tree) cxo.getChild(Tree.class);
		
		cxo = xo.getChild(SYMBIONT_TREE);
		final MutableTree symbiontTree = (MutableTree) cxo.getChild(Tree.class);
		
		final BranchRateModel branchRateModel = (BranchRateModel) xo.getChild(BranchRateModel.class);
		
		final Parameter origin = (Parameter) xo.getChild(Parameter.class);
		
		return new CophylogenyLikelihood(hostTree, symbiontTree, cophylogenyModel, branchRateModel, origin, reconstructionTagName, xo.getId());
	}


	@Override
	public XMLSyntaxRule[] getSyntaxRules() {
		return rules;
	}


	@Override
	public String getParserDescription() {
		return "This element represents the likelihood of the cophylogenetic mapping given the host and symbiont trees.";
	}


	@SuppressWarnings("rawtypes")
	@Override
	public Class getReturnType() {
		return CophylogenyLikelihood.class;
	}

	private final XMLSyntaxRule[] rules = {
			AttributeRule.newStringRule(RECONSTRUCTION_TAG_NAME),
			new ElementRule(CophylogenyModel.class),
			new ElementRule(HOST_TREE, new XMLSyntaxRule[]{
					new ElementRule(Tree.class)
			}),
			new ElementRule(SYMBIONT_TREE, new XMLSyntaxRule[]{
					new ElementRule(MutableTree.class)
			}),
			new ElementRule(BranchRateModel.class),
			new ElementRule(Parameter.class)
	};
	
}
