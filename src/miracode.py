# Miracode
# Copyright (C) 2022-2023 Idrees Hassan
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import fontforge
import json
import math
import argparse
from generate_diacritics import generateDiacritics
from generate_examples import generateExamples
from polygonizer import PixelImage, generatePolygons
from generate_continuous_ligatures import generate_continuous_ligatures 
from font_metadata import finalizeFont
from accent_shapes import drawSwedishAccent

PIXEL_SIZE = 256
SQRT_TWO = math.sqrt(2)
parser = argparse.ArgumentParser(description="Generate Miracode from its pixel source")
parser.add_argument("--style", choices=("Regular", "Bold"), default="Regular")
parser.add_argument("--test", action="store_true")
parser.add_argument("--punctuation-dots", choices=("original", "basic", "extended"), default="extended")
args = parser.parse_args()
STROKE = 312 if args.style == "Bold" else 192
PUNCTUATION_DIAMONDS = set(map(ord, '.:…' if args.punctuation_dots == 'basic' else
                             '.:;!?…·¡¿' if args.punctuation_dots == 'extended' else ''))

characters = json.load(open("./characters.json"))
characters.extend([
	{'codepoint': 0x25AA, 'name': 'black_small_square', 'pixels': [[0]]},
	{'codepoint': 0x25A0, 'name': 'black_square', 'pixels': [[0]]},
])
diacritics = json.load(open("./diacritics.json"))
ligatures = json.load(open("./ligatures.json"))
# ligatures += generate_continuous_ligatures("./continuous_ligatures.json")

characters = generateDiacritics(characters, diacritics)
charactersByCodepoint = {}
for character in characters:
	charactersByCodepoint[character["codepoint"]] = character

def generateFont():
	miracode = fontforge.font()
	miracode.fontname = "MiracodeText-Bold" if args.style == "Bold" else "MiracodeText-Regular"
	miracode.familyname = "Miracode Text"
	miracode.fullname = "Miracode Text Bold" if args.style == "Bold" else "Miracode Text Regular"
	miracode.copyright = "Idrees Hassan, https://github.com/IdreesInc/Miracode"
	miracode.encoding = "UnicodeFull"
	miracode.version = "1.13"
	miracode.weight = args.style
	miracode.ascent = PIXEL_SIZE * 8
	miracode.descent = PIXEL_SIZE
	miracode.em = PIXEL_SIZE * 9
	miracode.upos = -PIXEL_SIZE # Underline position
	miracode.addLookup("ligatures", "gsub_ligature", (), (("liga",(("dflt",("dflt")),("latn",("dflt")))),))
	miracode.addLookupSubtable("ligatures", "ligatures-subtable")
	miracode.addLookup("programming-calt", "gsub_ligature", (), (("calt",(("dflt",("dflt")),("latn",("dflt")))),))
	miracode.addLookupSubtable("programming-calt", "programming-calt-subtable")

	for character in characters:
		miracode.createChar(character["codepoint"], character["name"])
		glyph = miracode[character["name"]]
		if character["codepoint"] == 0x2026 and 0x2026 in PUNCTUATION_DIAMONDS:
			# Three distinct, stronger diamonds inside the single-cell advance.
			# The old seven-pixel source overhung the following code cell.
			pen = glyph.glyphPen()
			for center in (256, 768, 1280):
				drawDiamond(pen, center, 384, 248 if STROKE > 192 else 240)
		elif character["codepoint"] in (0x2022, 0x25E6, 0x25C6, 0x25C7):
			# Explicit vector list markers, centered on the capital body.
			# Both hollow and filled list diamonds now have sharp tips.
			if character["codepoint"] in (0x25E6, 0x25C7):
				drawDiamondRing(glyph.glyphPen(), 640, 1152, 320 if STROKE > 192 else 352)
			else:
				drawDiamond(glyph.glyphPen(), 640, 1152, 528 if STROKE > 192 else 480)
		elif character["codepoint"] in (0x25AA, 0x25A0):
			side = (448 if character["codepoint"] == 0x25AA else 960) + (120 if STROKE > 192 else 0)
			drawSquare(glyph.glyphPen(), 640, 1152, side)
		elif character["codepoint"] in (0xC5, 0xE5, 0xC4, 0xD6) or (character["codepoint"] == 65 and args.style == "Bold"):
			drawSwedishAccent(glyph, character["codepoint"], charactersByCodepoint,
			                  diacritics, drawCharacter, bold=args.style == "Bold")
		else:
			pen = glyph.glyphPen()
			if character.get("reference"):
				referencedCharacter = charactersByCodepoint[character["reference"]]
				drawCharacter(referencedCharacter, glyph, pen)
			else:
				drawCharacter(character, glyph, pen)

		if character["codepoint"] == 0x25CF:
			glyph.transform((1, 0, 0, 1, 0, 128))
		if "sideBearing" in character:
			# Fit an explicitly wide design inside one cell without changing
			# its vertical stroke thickness or the monospace advance.
			bearing = character["sideBearing"] * PIXEL_SIZE
			xMin, _, xMax, _ = glyph.boundingBox()
			scale = (PIXEL_SIZE * 6 - 2 * bearing) / (xMax - xMin)
			glyph.transform((scale, 0, 0, 1, bearing - xMin * scale, 0))
			glyph.round()
		glyph.width = PIXEL_SIZE * 6
	print(f"Generated {len(characters)} characters")

	outputDir = "../dist/"
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)

	# Generate the font without ligatures
	# print("Generating TTF font without ligatures...")
	# miracode.generate(outputDir + "Miracode-no-ligatures.ttf")

	for ligature in ligatures:
		if any(code in PUNCTUATION_DIAMONDS for code in ligature['sequence']):
			ligature['dotShape'] = 'diamond'
			ligature['largePunctuationDots'] = (320 if STROKE > 192 else 304) if any(code in map(ord, '!?¡¿') for code in ligature['sequence']) else (384 if STROKE > 192 else 352)
		lig = None
		if ligature.get("pixels"):
			# Basic ligature
			lig = miracode.createChar(-1, ligature["name"])
			pen = miracode[ligature["name"]].glyphPen()
			drawCharacter(ligature, lig, pen)
			miracode[ligature["name"]].width = PIXEL_SIZE * len(ligature["sequence"]) * 6
		elif ligature.get("chain"):
			# Chain ligature
			chain = ligature["chain"]
			lig = miracode.createChar(-1, ligature["name"])
			pen = miracode[ligature["name"]].glyphPen()
			xOffset = 0
			for character in chain:
				if character.get("pixels"):
					xOffset = drawCharacter({**character, 'dotShape': ligature.get('dotShape'), 'largePunctuationDots': ligature.get('largePunctuationDots')}, lig, pen, xOffset)
				elif character.get("reference"):
					linkedCharacter = charactersByCodepoint[character["reference"]]
					xOffset = drawCharacter({**linkedCharacter, 'largePunctuationDots': ligature.get('largePunctuationDots')}, lig, pen, xOffset)
				else:
					print(f"Unexpected character in ligature {ligature['name']}: {character}")
				xOffset += PIXEL_SIZE
		else:
			print(f"Unexpected ligature type: {ligature}")
			continue
		miracode[ligature["name"]].width = PIXEL_SIZE * len(ligature["sequence"]) * 6
		lig.addPosSub("ligatures-subtable", tuple(map(lambda codepoint: charactersByCodepoint[codepoint]["name"], ligature["sequence"])))
		if chr(ligature['sequence'][0]) in '!*+-/<=>':
			lig.addPosSub("programming-calt-subtable", tuple(charactersByCodepoint[c]["name"] for c in ligature['sequence']))

	print(f"Generated {len(ligatures)} ligatures")
	print("Generating TTF font...")
	output = outputDir + ("Miracode-Bold.ttf" if args.style == "Bold" else "Miracode.ttf")
	miracode.generate(output)
	finalizeFont(output, bold=args.style == "Bold")
	# print("Generating OTF font...")
	# miracode.generate(outputDir + "Miracode.otf")

def test():
	print("Testing...")
	tests = json.load(open("./tests.json"))["tests"]
	passedTests = 0
	failedTests = 0
	for test in tests:
		input = charactersByCodepoint[test["codepoint"]]["pixels"]
		output = test["output"]
		edgesPerPoint = getEdgesPerPoint(generateEdges(input))
		failed = []
		for row in range(len(input)):
			for col in range(len(input[0])):
				numOfEdges = len(edgesPerPoint.get((col, row), []))
				if output[row][col] != numOfEdges:
					failed.append(((row, col), output[row][col], numOfEdges))
		if len(failed) > 0:
			print(f"💥 Test failed: {test['character']}")
			for fail in failed:
				print(f"   Expected {fail[1]} edge(s) at {fail[0]}, got {fail[2]}")
			failedTests += 1
		else:
			# print (f"✅ Test passed: {test['character']}")
			passedTests += 1
	if failedTests == 0:
		print("All tests passed! 🎉")
	else:
		print(f"{failedTests} test(s) failed and {passedTests} tests passed")
		raise RuntimeError("Source geometry tests failed")


def get(pixel, row , col):
	if row < 0 or col < 0:
		return 0
	if row >= len(pixel) or col >= len(pixel[0]):
		return 0
	return pixel[row][col]

def compare(expected, actual):
	if expected == "~":
		return True
	elif expected == "1":
		return actual == 1
	elif expected == "0":
		return actual == 0
	return False

def matchPattern(pixels, row, col, pattern):
	cursorRow = None
	cursorCol = None
	for i in range(len(pattern)):
		for j in range(len(pattern[0])):
			if pattern[i][j] == "X":
				cursorRow = i
				cursorCol = j
				break
		if cursorRow != None:
			break
	if cursorRow == None or cursorCol == None:
		raise ValueError("Pattern must contain a cursor (X)")
	
	for i in range(len(pattern)):
		for j in range(len(pattern[0])):
			if i == cursorRow and j == cursorCol:
				continue
			if not compare(pattern[i][j], get(pixels, row + i - cursorRow, col + j - cursorCol)):
				return False
	return True

def generateEdges(pixels, drawDiagonals = True):
	edges = []

	numOfCols = len(pixels[0])
	numOfRows = len(pixels)
	for row in range(numOfRows):
		for col in range(numOfCols):
			if pixels[row][col] == 1:
				# Check if there is a pixel to the right
				if col < numOfCols - 1 and pixels[row][col + 1] == 1:
					if drawDiagonals and ignoreRight(pixels, row, col):
						pass
					else:
						edges.append(((col, row), (col + 1, row)))
				# Check if there is a pixel below
				if row < numOfRows - 1 and pixels[row + 1][col] == 1:
					if drawDiagonals and ignoreDown(pixels, row, col):
						pass
					else:
						edges.append(((col, row), (col, row + 1)))
				# Check diagonals
				if not drawDiagonals:
					continue
				# Check if there is a pixel to the bottom right
				if col < numOfCols - 1 and row < numOfRows - 1 and pixels[row + 1][col + 1] == 1:
					if not ignoreDiagonal(pixels, row, col, False):
						edges.append(((col, row), (col + 1, row + 1)))
				# Check if there is a pixel to the bottom left
				if col > 0 and row < numOfRows - 1 and pixels[row + 1][col - 1] == 1:
					if not ignoreDiagonal(pixels, row, col, True):
						edges.append(((col, row), (col - 1, row + 1)))
	return edges

def ignoreRight(pixels, row, col):
	ignorePatterns = [
		# "W" left
		(
			("1", "0", "1"),
			("X", "1", "0"),
			("1", "0", "~"),
		),
		# "W" right
		(
			("1", "0", "1"),
			("0", "X", "1"),
			("0", "0", "1"),
		),
		# "0"
		(
			("0", "0", "1"),
			("0", "X", "1"),
			("1", "0", "1"),
		),
		# "M"
		(
			("1", "0", "0"),
			("X", "1", "0"),
			("1", "0", "1"),
		),
		# "1"
		(
			("0", "0", "0"),
			("0", "1", "0"),
			("X", "1", "0"),
			("0", "1", "0"),
			("0", "1", "0"),
		),
	]
	for pattern in ignorePatterns:
		if matchPattern(pixels, row, col, pattern):
			return True
	return False

def ignoreDown(pixels, row, col):
	ignorePatterns = [
		# "z" top
		(
			("1", "X", "1"),
			("0", "1", "0"),
			("1", "0", "0"),
		),
		# "z" bottom
		(
			("0", "0", "1", "0"),
			("0", "X", "0", "0"),
			("1", "1", "1", "~"),
		),
		# "→", "->"
		(
			("1", "0", "0"),
			("0", "X", "0"),
			("1", "1", "1"),
			("0", "1", "0"),
			("1", "0", "0"),
		),
		# "←"
		(
			("0", "0", "1"),
			("0", "X", "0"),
			("1", "1", "1"),
			("0", "1", "0"),
			("0", "0", "1"),
		),
	]
	for pattern in ignorePatterns:
		if matchPattern(pixels, row, col, pattern):
			return True
	return False

def flipPattern(pattern):
	return list(map(lambda row: list(reversed(row)), pattern))

def ignoreDiagonal(pixels, row , col, flipped):
	whitelist = [
		# "z"
		(
			("X", "1", "1"),
			("0", "1", "0"),
			("0", "0", "1"),
		),
		# "↑"
		(
			("0", "0", "X", "0", "0"),
			("0", "1", "1", "1", "0"),
			("1", "0", "1", "0", "1"),
		),
		# "→", "->"
		(
			("1", "0", "0"),
			("0", "X", "0"),
			("1", "1", "1"),
			("0", "1", "0"),
			("1", "0", "0"),
		),
		# "↓"
		(
			("1", "0", "1", "0", "1"),
			("0", "X", "1", "1", "0"),
			("0", "0", "1", "0", "0"),
		),
	]
	blacklist = [
		(
			("0", "0", "0"),
			("X", "1", "0"),
			("0", "1", "0"),
		),
		# "H" left
		(
			("X", "0", "0"),
			("1", "1", "1"),
			("1", "0", "0"),
		),
		# "H" right and "#"
		(
			("~", "0", "1"),
			("1", "X", "1"),
			("~", "0", "1"),
		),
		# "f"
		(
			("0", "X", "0"),
			("1", "1", "1"),
			("0", "1", "0"),
		),
		# "z" top
		(
			("X", "1", "1"),
			("0", "1", "0"),
			("1", "0", "0"),
		),
		# "z" bottom
		(
			("0", "0", "1"),
			("0", "X", "0"),
			("1", "1", "1"),
		),
		# "k" and "h"
		(
			("X", "0", "1"),
			("1", "1", "~"),
			("1", "~", "~"),
		),
		# "l"
		(
			("0", "0", "0"),
			("0", "X", "1"),
			("0", "0", "1"),
			("0", "0", "1"),
		),
		# "u" and "w"
		(
			("0", "1", "0"),
			("0", "X", "0"),
			("~", "1", "1"),
		),
		# "0"
		(
			("0", "0", "1"),
			("~", "X", "1"),
			("~", "0", "1"),
		),
		# "F", "E", "P", etc.
		(
			("1", "X", "1"),
			("0", "0", "1"),
			("~", "~", "1"),
		),
		# "5"
		(
			("1", "1"),
			("X", "0"),
			("1", "1"),
		),
		# "Z"
		(
			("0", "0", "1", "0"),
			("0", "X", "0", "0"),
			("0", "1", "1", "1"),
		),
		# "$" top
		(
			("0", "0", "0"),
			("0", "X", "0"),
			("1", "1", "1"),
		),
		# "$" bottom
		(
			("X", "1", "1"),
			("0", "1", "0"),
			("0", "0", "0"),
		),
		# "e"
		(
			("0", "1", "1"),
			("X", "0", "0"),
			("1", "1", "1"),
		),
		# "2"
		(
			("0", "0", "0"),
			("0", "X", "0"),
			("0", "1", "1"),
			("0", "0", "0"),
		),
	]
	for pattern in whitelist:
		pat = pattern
		if flipped:
			pat = flipPattern(pattern)
		if matchPattern(pixels, row, col, pat):
			return False
	for pattern in blacklist:
		pat = pattern
		if flipped:
			pat = flipPattern(pattern)
		if matchPattern(pixels, row, col, pat):
			return True
	return False

def countNeighbors(pixels, row, col):
	count = 0
	if get(pixels, row - 1, col) == 1:
		count += 1
	if get(pixels, row, col - 1) == 1:
		count += 1
	if get(pixels, row + 1, col) == 1:
		count += 1
	if get(pixels, row, col + 1) == 1:
		count += 1
	if get(pixels, row - 1, col - 1) == 1:
		count += 1
	if get(pixels, row - 1, col + 1) == 1:
		count += 1
	if get(pixels, row + 1, col - 1) == 1:
		count += 1
	if get(pixels, row + 1, col + 1) == 1:
		count += 1
	return count

def drawCircle(pen, x, y, radius):
	# Draw clockwise
	VAL = 0.5522847498 # This is (4/3) * (sqrt(2) - 1)
	pen.moveTo(x, y + radius)
	pen.curveTo(x + radius * VAL, y + radius, x + radius, y + radius * VAL, x + radius, y)
	pen.curveTo(x + radius, y - radius * VAL, x + radius * VAL, y - radius, x, y - radius)
	pen.curveTo(x - radius * VAL, y - radius, x - radius, y - radius * VAL, x - radius, y)
	pen.curveTo(x - radius, y + radius * VAL, x - radius * VAL, y + radius, x, y + radius)
	pen.closePath()


def drawOctagon(pen, x, y, radius):
	# Draw clockwise
	VAL = (1 + SQRT_TWO) / 2
	sideLength = radius / VAL
	OCTAGON = [
		(1/2, VAL),
		(VAL, 1/2),
		(VAL, -1/2),
		(1/2, -VAL),
		(-1/2, -VAL),
		(-VAL, -1/2),
		(-VAL, 1/2),
		(-1/2, VAL)
	]
	pen.moveTo(x + sideLength * OCTAGON[0][0], y + sideLength * OCTAGON[0][1])
	for i in range(1, len(OCTAGON)):
		pen.lineTo(x + sideLength * OCTAGON[i][0], y + sideLength * OCTAGON[i][1])
	pen.closePath()

def drawSquare(pen, x, y, side):
	half = side / 2
	pen.moveTo(x - half, y + half)
	for px, py in [(half, half), (half, -half), (-half, -half)]:
		pen.lineTo(x + px, y + py)
	pen.closePath()

def drawDiamond(pen, x, y, radius):
	pen.moveTo(x, y + radius)
	for px, py in [(radius, 0), (0, -radius), (-radius, 0)]:
		pen.lineTo(x + px, y + py)
	pen.closePath()

def drawDiamondRing(pen, x, y, inner):
	# Larger, sharp diamond tips, independent of the unchanged letter rings.
	radius = 576 if STROKE > 192 else 544
	outer = [(0, radius), (radius, 0), (0, -radius), (-radius, 0)]
	pen.moveTo(x + outer[0][0], y + outer[0][1])
	for px, py in outer[1:]:
		pen.lineTo(x + px, y + py)
	pen.closePath()
	# Opposite winding makes an actual transparent counter, never a white fill.
	pen.moveTo(x, y + inner)
	for px, py in [(-inner, 0), (0, -inner), (inner, 0)]:
		pen.lineTo(x + px, y + py)
	pen.closePath()

def drawHeart(pen, x, y, radius):
	# Draw clockwise
	HEART = [
		(0, 0.9),
		(0.8, 1.6),
		(1.6, 0.9),
		(1.6, 0.2),
		(0, -1),
		(-1.6, 0.2),
		(-1.6, 0.9),
		(-0.8, 1.6)
	]
	SCALE = 1.3
	radius *= SCALE
	pen.moveTo(x + radius * HEART[0][0], y + radius * HEART[0][1])
	for i in range(1, len(HEART)):
		pen.lineTo(x + radius * HEART[i][0], y + radius * HEART[i][1])
	pen.closePath()

def getEdgesPerPoint(edges):
	edgesPerPoint = {}
	for edge in edges:
		if edge[0] not in edgesPerPoint:
			edgesPerPoint[edge[0]] = []
		edgesPerPoint[edge[0]].append(edge)
		if edge[1] not in edgesPerPoint:
			edgesPerPoint[edge[1]] = []
		edgesPerPoint[edge[1]].append(edge)
	return edgesPerPoint

def drawCharacter(character, glyph, pen, xOffset = 0, stroke = None):
	# print("Drawing character", character["name"])
	if not character.get("pixels"):
		# print(f"Character {character['name']} has no pixels")
		return xOffset
	drawDiagonals = True
	if "diagonals" in character:
		drawDiagonals = character["diagonals"]
	edges = generateEdges(character["pixels"], drawDiagonals)

	edgesPerPoint = getEdgesPerPoint(edges)

	descent = 0
	if "descent" in character:
		descent = character["descent"]
	top = (len(character["pixels"]) - descent) * PIXEL_SIZE

	leftMargin = 0
	if "leftMargin" in character:
		leftMargin += character["leftMargin"]
	left = leftMargin * PIXEL_SIZE + xOffset

	HALF = (STROKE if stroke is None else stroke) / 2
	DOT_RADIUS = HALF * 1.5

	# Draw the paths
	for edge in edges:
		startX = edge[0][0] * PIXEL_SIZE + PIXEL_SIZE / 2 + left
		startY = top - (edge[0][1] * PIXEL_SIZE - PIXEL_SIZE / 2)
		endX = edge[1][0] * PIXEL_SIZE + PIXEL_SIZE / 2 + left
		endY = top - (edge[1][1] * PIXEL_SIZE - PIXEL_SIZE / 2)
		if startX == endX:
			# Down
			pen.moveTo(startX - HALF, startY)
			pen.lineTo(startX + HALF, startY)
			pen.lineTo(startX + HALF, endY)
			pen.lineTo(startX - HALF, endY)
			pen.closePath()
		elif startY == endY:
			# Right
			pen.moveTo(startX, startY - HALF)
			pen.lineTo(startX, startY + HALF)
			pen.lineTo(endX, startY + HALF)
			pen.lineTo(endX, startY - HALF)
			pen.closePath()
		elif startX < endX:
			# Diagonal right
			pen.moveTo(startX - HALF / SQRT_TWO, startY - HALF / SQRT_TWO)
			pen.lineTo(startX + HALF / SQRT_TWO, startY + HALF / SQRT_TWO)
			pen.lineTo(endX + HALF / SQRT_TWO, endY + HALF / SQRT_TWO)
			pen.lineTo(endX - HALF / SQRT_TWO, endY - HALF / SQRT_TWO)
			pen.closePath()
		else:
			# Diagonal left
			pen.moveTo(startX - HALF / SQRT_TWO, startY + HALF / SQRT_TWO)
			pen.lineTo(startX + HALF / SQRT_TWO, startY - HALF / SQRT_TWO)
			pen.lineTo(endX + HALF / SQRT_TWO, endY - HALF / SQRT_TWO)
			pen.lineTo(endX - HALF / SQRT_TWO, endY + HALF / SQRT_TWO)
			pen.closePath()


	jointAtPoint = {}
	# Calculate if each point has any joints that aren't in a straight line
	# For instance, a joint coming from the left and a joint coming from the top or just a joint coming from the left
	for point, edges in edgesPerPoint.items():
		if len(edges) == 1:
			# End cap
			jointAtPoint[point] = 1
		elif len(edges) == 2:
			# Determine if the edges are in a straight line
			edge1 = edges[0]
			edge2 = edges[1]
			if edge1[0][0] == edge1[1][0] and edge2[0][0] == edge2[1][0]:
				# Vertical
				jointAtPoint[point] = 0
			elif edge1[0][1] == edge1[1][1] and edge2[0][1] == edge2[1][1]:
				# Horizontal
				jointAtPoint[point] = 0
		else:
			# Joint
			jointAtPoint[point] = 1

	# Draw the dots
	pixels = character["pixels"]
	for row in range(len(pixels)):
		for col in range(len(pixels[0])):
			x = col * PIXEL_SIZE + PIXEL_SIZE / 2 + left
			y = top - row * PIXEL_SIZE + PIXEL_SIZE / 2
			if pixels[row][col] == 1:
				if countNeighbors(pixels, row, col) == 0:
					# Isolated dot
					if character.get("codepoint") in (105, 106):
						# Text-size i/j dots need an open gap even in 10px Bold.
						# Keep the source stem and baseline; balance dot area
						# separately from stroke expansion and lift it slightly.
						lift = 160 if STROKE > 192 else 96
						drawDiamond(pen, x, y + lift, 164 if STROKE > 192 else 144)
					else:
						# Preserve every other accent, quote and comma. Optional
						# punctuation studies select explicit codepoints only.
						if character.get('dotShape') == 'diamond' or character.get('codepoint') in ({0xE4, 0xF6} | PUNCTUATION_DIAMONDS):
							code = character.get('codepoint')
							if character.get('largePunctuationDots'):
								radius = character['largePunctuationDots']
							elif code in PUNCTUATION_DIAMONDS:
								radius = (320 if STROKE > 192 else 304) if code in map(ord, '!?¡¿') else (384 if STROKE > 192 else 352)
							else:
								radius = 216 if STROKE > 192 else 176
							drawDiamond(pen, x, y, radius)
						else:
							drawCircle(pen, x, y, DOT_RADIUS)
					continue
				elif jointAtPoint.get((col, row)) == 0:
					# No joint or end cap
					continue
				drawOctagon(pen, x, y, HALF)
			elif pixels[row][col] == 2:
				# Heart
				drawHeart(pen, x, y, HALF)

	# Merge intersecting paths
	glyph.simplify()
	glyph.round()
	glyph.removeOverlap()

	# Return the rightmost edge of the character
	return xOffset + len(pixels[0]) * PIXEL_SIZE

if args.test:
	test()
else:
	generateFont()
	generateExamples(characters, ligatures, charactersByCodepoint)
	test()
