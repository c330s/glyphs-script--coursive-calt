#MenuTitle: Build positional calt feature for coursive type
# -*- coding: utf-8 -*-
__doc__="""
Create calt for positional forms with .isol, .init, .medi, .fina suffixes.
"""

import GlyphsApp
thisFont = Glyphs.font
positionalFeature = "calt"
anyLetterClassName = "AnyLetter"
extensionDef = "Def"
extensionSub = "Sub"
ignoreStatements = {
	"isol": "ignore sub @isol%s' @%s, @%s @isol%s';" % ( extensionDef, anyLetterClassName, anyLetterClassName, extensionDef ),
	"high": "sub @high%s by @high%s;" % ( extensionDef, extensionDef ),
	"highfina": " ignore sub @highfinaDef' @AnyLetter; \n\tsub @highDef @highfina%s' by @highfina%s;" % ( extensionDef, extensionSub),
	"fina": "ignore sub @fina%s' @%s;" % ( extensionDef, anyLetterClassName ),
	"highmedi": "sub @highDef @highmedi%s' @%s by @highmedi%s; \n\tsub @highDefmedi @highmedi%s' @%s by @highmedi%s;" % (extensionDef, anyLetterClassName, extensionSub, extensionDef, anyLetterClassName, extensionSub ),
	"medi": "sub @%s @medi%s' @%s by @medi%s;" % ( anyLetterClassName, extensionDef, anyLetterClassName, extensionSub ),
	"init": "ignore sub @%s @init%s';" % ( anyLetterClassName, extensionDef )
}
suffixes = [
	"isol",
	"high",
	"highfina",
	"fina",
	"highmedi",
	"medi",
	"init"
]

def updated_code( oldcode, beginsig, endsig, newcode ):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find( beginsig )
	end_offset   = oldcode.find( endsig ) + len( endsig )
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode

def create_otfeature( featureName = "calt",
                      featureCode = "# empty feature code",
                      targetFont  = None,
                      codeSig     = "DEFAULT-CODE-SIGNATURE" ):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	"""

	if targetFont:
		beginSig = "# BEGIN " + codeSig + "\n"
		endSig   = "# END "   + codeSig + "\n"

		if featureName in [ f.name for f in targetFont.features ]:
			# feature already exists:
			targetFeature = targetFont.features[ featureName ]

			if beginSig in targetFeature.code:
				# replace old code with new code:
				targetFeature.code = updated_code( targetFeature.code, beginSig, endSig, featureCode )
			else:
				# append new code:
				targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig

			return "Updated existing OT feature '%s'." % featureName
		else:
			# create feature with new code:
			newFeature = GSFeature()
			newFeature.name = featureName
			newFeature.code = beginSig + featureCode + "\n" + endSig
			targetFont.features.append( newFeature )
			return "Created new OT feature '%s'" % featureName
	else:
		return "ERROR: Could not create OT feature %s. No font detected." % ( featureName )

def create_otclass( className       = "@default",
                    classGlyphNames = [],
                    targetFont      = None ):
	"""
	Creates an OpenType class in the font.
	Default: class @default with currently selected glyphs in the current font.
	Returns a status message in form of a string.
	"""

	if targetFont and classGlyphNames:
		# strip '@' from beginning:
		if className[0] == "@":
			className = className[1:]

		classCode = " ".join( classGlyphNames )

		if className in [ c.name for c in targetFont.classes ]:
			targetFont.classes[className].code = classCode
			return "Updated existing OT class '%s'." % ( className )
		else:
			newClass = GSClass()
			newClass.name = className
			newClass.code = classCode
			targetFont.classes.append( newClass )
			return "Created new OT class: '%s'" % ( className )
	else:
		return "ERROR: Could not create OT class %s. Missing either font or glyph names, or both." % ( className )

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print "Building positional calt feature:"

# ?? Erzeugt ein Array aller exportierten Glyphen der Kategorie Letter
allLetterNames = [ g.name for g in thisFont.glyphs if g.category == "Letter" and g.export ]

print "\t%s" % create_otclass(
	className       = anyLetterClassName,
	classGlyphNames = allLetterNames,
	targetFont      = thisFont
)

positionalFeatureCode = "\n"

for thisSuffix in suffixes:
	dotSuffix = "." + thisSuffix
	dotSuffixLength = len( dotSuffix )
	theseSuffixedGlyphNames = [ g.name for g in thisFont.glyphs if g.name.endswith( dotSuffix ) and ( thisFont.glyphs[g.name[:-dotSuffixLength]] is not None ) ]
	theseUnsuffixedGlyphNames = [ n[:-dotSuffixLength] for n in theseSuffixedGlyphNames ]

	print "\tFound %i glyphs with a %s suffix, and %i unsuffixed counterparts." % (
		len( theseSuffixedGlyphNames ),
		dotSuffix,
		len( theseUnsuffixedGlyphNames )
	)

	if len( theseSuffixedGlyphNames ) > 0:
		print "\t%s" % create_otclass(
			className       = thisSuffix + extensionDef,
			classGlyphNames = theseUnsuffixedGlyphNames,
			targetFont      = thisFont
		)
		print "\t%s" % create_otclass(
			className       = thisSuffix + extensionSub,
			classGlyphNames = theseSuffixedGlyphNames,
			targetFont      = thisFont
		)

		thisIgnoreCode = ignoreStatements[ thisSuffix ]

		if thisIgnoreCode.startswith( "ignore" ):
			ignoreSubstitution = "\tsub @%s%s' by @%s%s;\n" % (
				thisSuffix,
				extensionDef,
				thisSuffix,
				extensionSub
			)
		else:
			ignoreSubstitution = ""

		positionalFeatureCode += "lookup %sForms {\n" % ( thisSuffix.title() )
		positionalFeatureCode += "\t%s\n" % ( thisIgnoreCode )
		positionalFeatureCode += ignoreSubstitution
		positionalFeatureCode += "} %sForms;\n\n" % ( thisSuffix.title() )


# Begin My Shitty Code

	"""
	Alle Glyphen finden, die sowohl in highmediDef, als auch in highDef vorkommen.
	Diese Glyphen ergeben die neue OT-Klasse highDefmedi (Basisglyph.highmedi).
	"""

highmediSuffix = ".highmedi"
highmediSuffixLength = len( highmediSuffix )

highSuffix = ".high"
highSuffixLength = len( highSuffix )

highDefmedi = []

# alle Glyphen mit Suffix .highmedi
highmediDefSuffixedGlyphNames = [g.name for g in thisFont.glyphs if g.name.endswith( highmediSuffix ) and (thisFont.glyphs[g.name[:-highmediSuffixLength]] is not None ) ]

# Alle .highmedi-Basis-Glyphen
highmediDefUnSuffixedGlyphNames = [ n[:-highmediSuffixLength] for n in highmediDefSuffixedGlyphNames ]

# Alle Glyphen mit Suffix .high
highDefSuffixedGlyphNames = [h.name for h in thisFont.glyphs if h.name.endswith( highSuffix ) and (thisFont.glyphs[h.name[:-highSuffixLength]] is not None ) ]

# Alle .high-Basis-Glyphen
highDefUnSuffixedGlyphNames = [ o[:-highSuffixLength] for o in highDefSuffixedGlyphNames ]

for i in highmediDefUnSuffixedGlyphNames:
#	print i
	for j in highDefUnSuffixedGlyphNames:
#		message = "\t%s" % (j)
#		print message
		if i == j:
			newValue = i + highmediSuffix
#			print newValue
			highDefmedi.append(newValue)
#			print highDefmedi


# ########

print "\t%s" % create_otclass (
	className		= "highDefmedi",
	classGlyphNames	= highDefmedi,
	targetFont		= thisFont
)

# End My Shitty Code


print "\t%s" % create_otfeature(
	featureName = positionalFeature,
	featureCode = positionalFeatureCode,
	targetFont  = thisFont,
	codeSig     = "POSITIONAL ALTERNATES"
)
