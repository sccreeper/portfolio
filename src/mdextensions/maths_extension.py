from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
import re
from latex2mathml.converter import convert_to_element

INLINE_MATHS_REGEX_COMPLETE = r"\$(.+?)\$"


class InlineMathsPattern(InlineProcessor):
    def handleMatch(self, m, data):

        # Gather latex string and parse
        latex_parsed = convert_to_element(m.group(1))

        return latex_parsed, m.start(0), m.end(0)

    def getCompiledRegExp(self):
        return re.compile(INLINE_MATHS_REGEX_COMPLETE)


class BlockMathsProcessor(BlockProcessor):
    RE_FENCE_START = r"^\${2}"
    RE_FENCE_END = r"\${2}"

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_FENCE_START, "", blocks[0])

        for i, block in enumerate(blocks):
            blocks[i] = re.sub(self.RE_FENCE_END, "", block)

            # Gather latex string and parse
            latex_parsed = convert_to_element(
                " ".join(blocks[0 : i + 1]), display="block"
            )

            parent.append(latex_parsed)

            # Remove rest remaining blocks
            for j in range(0, i + 1):
                blocks.pop(0)

            return True

        blocks[0] = original_block
        return False


class MathsExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            InlineMathsPattern(INLINE_MATHS_REGEX_COMPLETE, md), "inline_maths", 75
        )

        md.parser.blockprocessors.register(BlockMathsProcessor(md.parser), "block_maths", 75)
