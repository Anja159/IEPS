
# from bs4 import BeautifulSoup
import re
import os
import sys
import codecs
from bs4 import BeautifulSoup, NavigableString, Comment
import difflib as dl

# self_closing_tags = ["area", "base", "br", "col", "embed", "hr",
#                      "img", "input", "link", "meta", "param", "source", "track", "wbr"]
# ignore_tags = ["b", "script", "br", "em", "hr"]


# def cleanup_html(soup):
#     for script in soup.body.find_all('script'):
#         script.decompose()  # remove all script tags
#     return soup.prettify()


# def build_DOM_tree(text):
#     # 1: cleanup html tags, enclose open tags...
#     clean_html = cleanup_html(BeautifulSoup(text, "lxml"))

#     # 2. build tree
#     tree = BeautifulSoup(clean_html, "lxml")

#     return tree


# def get_repeating_tag(tag_name, items_list, current_idx):
#     num_of_opening_tags = 1
#     repeating_part = [items_list[current_idx][1].name]
#     while num_of_opening_tags > 0 and current_idx < len(items_list) - 1:
#         current_idx = current_idx + 1
#         next_item = items_list[current_idx][1]
#         tag = items_list[current_idx][0]  # < or /
#         # is td=tr?
#         if next_item.name == tag_name:
#             # another open <tr>
#             if tag == "<":
#                 num_of_opening_tags += 1
#             else:
#                 num_of_opening_tags -= 1
#         repeating_part.append(tag + next_item.name)
#     return repeating_part, current_idx


# # Recursive function that builds list from tree, maybe not the best solution, as we later find out...

# def construct_tag_list(source, path):

#     # HERE TAG IS OPENED
#     if source.name not in ignore_tags:
#         path.append(("<", source))

#     # TAG DOES NOT HAVE LOWER LEVELS
#     if not source.find_all(recursive=False):
#         # leaf node, backtrack, close tag...
#         if source.name not in self_closing_tags and source.name not in ignore_tags:
#             path.append(("</", source))
#             pass
#         return path

#     # FOR EVERY TAGS CHILD
#     for child1 in source.children:
#         if not isinstance(child1, NavigableString):
#             path = construct_tag_list(child1, path)

#     # HERE TAG IS CLOSED
#     if source.name not in self_closing_tags and source.name not in ignore_tags:
#         path.append(("</", source))
#         pass
#     return path


# def check_tags_text(tag1, tag2):
#     if tag1.name in ignore_tags or tag2.name in ignore_tags:
#         return
#     text_tags1 = tag1.findAll(text=True, recursive=False)
#     text_tags2 = tag2.findAll(text=True, recursive=False)
#     text1_list = []
#     text2_list = []
#     # Tried with regex but failed, ALSO stripped_strings exists :/
#     for a in text_tags1:
#         # Ignore comment tags text
#         if not isinstance(a, Comment) and len(a.strip()) > 0:
#             text1_list.append(a.strip())
#     for a in text_tags2:
#         if not isinstance(a, Comment) and len(a.strip()) > 0:
#             text2_list.append(a.strip())
#     if text1_list == text2_list:
#         for i in text1_list:
#             print(i, end="  ")
#     else:
#         print("#TEXT", end="  ")

#     return


# def compare_tag_lists(list1, list2):
#     """lists of tuples ('<', tag)"""
#     print("<html>  <head>  </head>", end="  ")
#     # Indices list of matching element from other list
#     i = 0
#     j = 0
#     while i < len(list1) and j < len(list2):
#         tag1 = list1[i][1]  # Tag is second element in tuple, stupid
#         tag2 = list2[j][1]
#         if tag1.name == tag2.name:
#             # TAG MATCH
#             # print(list1[i][0], tag1.name, "  ", list2[j][0],tag2.name)
#             # opening tag, print to output
#             print(list1[i][0] + tag1.name + ">", end="  ")

#             # IF TAGS MATCH CHECK THEIR TEXT
#             if list1[i][0] != "</":
#                 check_tags_text(tag1, tag2)

#         else:
#             # TAG MISMATCH, find closing tag
#             prev_tag_name_list1 = get_previous_tag_name(list1, i)
#             prev_tag_name_list2 = get_previous_tag_name(list2, j)

#             # print(list1[i], "  ", list2[j], " MISMATCHTAG", " prev1: ", prev_tag_name_list1)

#             # check if repeating : in WRAPPER - LIST GOES ON, e.g. <tr> (and sample has </tbody>)
#             if tag1.name == prev_tag_name_list1:
#                 # wrapper iterator?
#                 square_candidate, new_idx = get_repeating_tag(
#                     prev_tag_name_list1, list1, i)
#                 i = new_idx + 1
#                 print("(<", end="")
#                 for n in square_candidate:
#                     if n[0] == "</":
#                         print("<"+n+">", end="")
#                     else:
#                         print(n+">", end="")
#                 print(")?", end="  ")
#                 continue

#             # SAMPLE is repeating
#             if tag2.name == prev_tag_name_list2:
#                 # sample iterator?
#                 square_candidate, new_idx = get_repeating_tag(
#                     prev_tag_name_list2, list2, j)
#                 j = new_idx + 1
#                 print("(<", end="")
#                 for n in square_candidate:
#                     if n[0] == "</":
#                         print("<" + n + ">", end="")
#                     else:
#                         print(n + ">", end="")
#                 print(")?")
#                 continue

#         i += 1
#         j += 1
#     print("</html>  ")
#     return


# def get_previous_tag_name(items_list, current_index):
#     current_index -= 1
#     tag = items_list[current_index][1].name
#     return tag


# def roadrunner(text1, text2):
#     # Site 1 is set as reg. expression wrapper. Update and generalize it by using the second (third, fourth,...) one.
#     tree1 = build_DOM_tree(text1)
#     tree2 = build_DOM_tree(text2)

#     # Here you construct regex from first trees
#     tag_list1 = construct_tag_list(tree1.body, [])
#     tag_list2 = construct_tag_list(tree2.body, [])

#     compare_tag_lists(tag_list1, tag_list2)
#     return


# def main():
#     # Temporary
#     f1 = codecs.open(
#         os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
#                      'input-extraction', 'overstock.com', 'jewelry01.html'),
#         'r',  encoding='iso-8859-1')
#     f2 = codecs.open(
#         os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'input-extraction', 'overstock.com',
#                      'jewelry02.html'),
#         'r',  encoding='iso-8859-1')
#     text1 = f1.read()
#     text2 = f2.read()

#     # Result is a union-free regular expression
#     roadrunner(text1, text2)


# if __name__ == "__main__":
#     main()

def tokenize_html(page):
    with open(page) as bs:
        soup = BeautifulSoup(bs, "html.parser")
        tokens = []
        for tag in soup.find_all():
            if tag.name:
                tokens.append(("initial_tag", tag.name))
            if tag.string and tag.string.strip():
                tokens.append(("data", tag.string.strip().lower()))
            if tag.name:
                tokens.append(("terminal_tag", tag.name))

    return tokens


def clean_wrapper_iterators(wrapper, iterator_tag, internal_wrapper):
    # Implementation remains the same as before
    pass


def generate_wrapper(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    wrapper = {}

    # Example: find all <p> tags and create a regex to extract their content
    p_tags = soup.find_all('p')
    wrapper['<p>'] = '|'.join([re.escape(tag.text) for tag in p_tags])

    # Add more rules based on your analysis of the HTML structure

    return wrapper


def solve_mismatches(wrapper, html_content):
    # This function should generalize the existing wrapper based on the mismatches with the new page
    # Implement the logic to solve mismatches here
    pass


def roadrunner(wrapper_tokens, sample_tokens, indx_w, indx_s, wrapper):
    # Initialize the wrapper with a random page's structure
    wrapper = generate_wrapper(html_pages[0])

    # Iterate through the remaining pages to generalize the wrapper
    for html_content in html_pages[1:]:
        # Solve mismatches with the current page
        solve_mismatches(wrapper, html_content)

    return wrapper


def autoExtract(pages):
    # """ READ INPUT FILES """
    # with open('../data/test_pages/wrapper_page.html') as wrapper_file:
    #     wrapper_page = wrapper_file.read()

    # with open('../data/test_pages/sample_page.html') as sample_file:
    #     sample_page = sample_file.read()

    kitaraHtml1 = pages[0]
    kitaraHtml2 = pages[1]

    """ TOKENIZE HTML PAGES """
    # for page in pages:
    kitaraToken1 = tokenize_html(kitaraHtml1)
    kitaraToken2 = tokenize_html(kitaraHtml2)

    # extractedTokens[idx] = wrapper
    # idx += 1

    """ RUN ROADRUNNER """
    # wrapper = roadrunner(wrapper_tokens, sample_tokens, 0, 0, [])
    print(kitaraToken1)
    print('---------------------------')
    print(kitaraToken2)
    # ufre = write_final_wrapper_as_ufre(wrapper)
    # print(ufre)


# from html.parser import HTMLParser


# class HTMLParser(HTMLParser):
#     def __init__(self):
#         HTMLParser.__init__(self)
#         self.page

# class RunnerHTMLParser(HTMLParser):

#     def __init__(self):
#         HTMLParser.__init__(self)
#         self.page_tokens = []

#     def handle_starttag(self, tag, attrs):
#         self.page_tokens.append(["initial_tag", tag])
#         # print("< " + tag + " >")

#     def handle_endtag(self, tag):
#         self.page_tokens.append(["terminal_tag", tag])
#         # print("</" + tag + " >")

#     def handle_data(self, data):
#         data = data.strip().lower()
#         if data:
#             self.page_tokens.append(["data", data])
#         # print(data)

#     def clear_page_tokens(self):
#         self.page_tokens = []


# def read_html_code(path_html_file):

#     with open(path_html_file) as html_doc:
# 	    html_page = html_doc.read()

#     return html_page


# def get_iterator_string(iterator):

#     str_iter = "( "

#     for token in iterator:
#         if token[0] == "initial_tag":
#             str_iter += "".join(["<", token[1], ">"])
#         elif token[0] == "terminal_tag":
#             str_iter += "".join(["</", token[1], ">"])
#         elif token[0] == "optional":
#             str_iter += token[1]+""
#         else:
#             str_iter += token[1]

#     str_iter += " )+\n"

#     return str_iter


# def get_optional_string(optional):

#     str_opt = "( "

#     for token in optional:
#         if token[0] == "initial_tag":
#             str_opt += "".join(["<", token[1], ">"])
#         elif token[0] == "terminal_tag":
#             str_opt += "".join(["</", token[1], ">"])
#         elif token[0] == "optional":
#             str_opt += token[1]+""
#         else:
#             str_opt += token[1]

#     str_opt += " )?\n"

#     return str_opt


# def write_final_wrapper_as_ufre(wrapper):

#     ufre = ""

#     for token in wrapper:
#         if token[0] == "initial_tag":
#             ufre += "".join(["<", token[1], ">\n"])
#         elif token[0] == "terminal_tag":
#             ufre += "".join(["</", token[1], ">\n"])
#         elif token[0] == "optional":
#             ufre += token[1]+"\n"
#         elif token[0] == "iterator":
#             ufre += get_iterator_string(token[1])
#         else:
#             ufre += token[1]+"\n"

#     return ufre


# def matching_tokens(token_1, token_2):

#     if token_1[0] == token_2[0] and token_1[1] == token_2[1]:
#         return True
#     elif token_1[0] == "optional" and token_1[1][1:-2] == token_2[1]:
#         print("OPTIONAL MATCHING - MIGHT REQUIRE ADDITIONAL ATTENTION")
#         return True

#     return False


# def find_iterator_end(tokens, start_indx):

#     end_tag_found = False
#     i = start_indx

#     while i < len(tokens):

#         if tokens[i][0] == "terminal_tag" and tokens[i][1] == tokens[start_indx][1]:
#             end_tag_found = True
#             break

#         i += 1

#     return end_tag_found, i


# def find_prev_iterator_start(tokens, start_indx):

#     start_tag_found = False
#     i = start_indx

#     while i > 0:

#         if tokens[i][0] == "initial_tag" and tokens[i][1] == tokens[start_indx][1]:
#             start_tag_found = True
#             break

#         i -= 1

#     return start_tag_found, i


# def find_end_of_optional(tokens, start_indx, tag):

#     i = start_indx
#     found = False

#     while i < len(tokens)-1:

#         if tokens[i][0] == "terminal_tag" and tokens[i][1] == tag:
#             found = True
#             break

#         i += 1

#     return found, i


# def clean_wrapper_iterators(wrapper, iterator_tag, internal_wrapper):

#     i = len(wrapper)-1

#     new_end = None

#     while i > 0:

#         while i > 0 and wrapper[i][0] == "optional":
#             i -= 1

#         if wrapper[i][0] == "terminal_tag" and wrapper[i][1] == iterator_tag:

#             while i > 0:

#                 if wrapper[i][0] == "initial_tag" and wrapper[i][1] == iterator_tag:
#                     new_end = i
#                     i -= 1
#                     break
#                 i -= 1
#         else:
#             break

#     if new_end is None:
#         return wrapper

#     # we found new wrapper
#     wrapper = wrapper[:new_end]
#     new_iterator = ["iterator", internal_wrapper]
#     wrapper.append(new_iterator)

#     return wrapper


# def roadrunner(wrapper_tokens, sample_tokens, indx_w, indx_s, wrapper):

#     if indx_w == len(wrapper_tokens) and indx_s == len(sample_tokens):
#         # successful matching
#         return wrapper

#     wrap_token = wrapper_tokens[indx_w]
#     smpl_token = sample_tokens[indx_s]

#     # IF MATCHING TOKENS, SIMPLY APPEND TO THE WRAPPER
#     if matching_tokens(wrap_token, smpl_token):
#         wrapper.append(wrap_token)
#         return roadrunner(wrapper_tokens, sample_tokens, indx_w+1, indx_s+1, wrapper)
#     else:
#         # handle string mismatch:
#         if wrap_token[0] == "data" and smpl_token[0] == "data":
#             wrapper.append(["data", "#PCDATA"])
#             return roadrunner(wrapper_tokens, sample_tokens, indx_w+1, indx_s+1, wrapper)
#         # tag mismatch - either an optional or an iterative
#         else:
#             iterative = True

#             # check for iterative
#             prev_wrap_token = wrapper_tokens[indx_w-1]
#             prev_smpl_token = sample_tokens[indx_s-1]

#             # iterator discovered on wrapper side
#             if prev_wrap_token[0] == "terminal_tag" and wrap_token[0] == "initial_tag" and prev_wrap_token[1] == wrap_token[1]:
#                 # confirm existance of equal terminal tag
#                 iter_found, iter_end_indx = find_iterator_end(
#                     wrapper_tokens, indx_w)

#                 if iter_found:

#                     prev_iter_found, prev_iter_start_indx = find_prev_iterator_start(
#                         wrapper_tokens, indx_w-1)

#                     if prev_iter_found:

#                         prev_square = wrapper_tokens[prev_iter_start_indx:indx_w]
#                         square = wrapper_tokens[indx_w:iter_end_indx+1]

#                         internal_wrapper = roadrunner(
#                             prev_square, square, 0, 0, [])

#                         if internal_wrapper is not None:
#                             new_wrapper = clean_wrapper_iterators(
#                                 wrapper, wrap_token[1], internal_wrapper)
#                             return roadrunner(wrapper_tokens, sample_tokens, indx_w, iter_end_indx+1, new_wrapper)

#                         else:
#                             iterative = False
#                     else:
#                         iterative = False

#                 else:
#                     iterative = False

#             # iterator discovered on sample side
#             elif prev_smpl_token[0] == "terminal_tag" and smpl_token[0] == "initial_tag" and prev_smpl_token[1] == smpl_token[1]:
#                 # confirm existance of equal terminal tag
#                 iter_found, iter_end_indx = find_iterator_end(
#                     sample_tokens, indx_s)

#                 if iter_found:

#                     prev_iter_found, prev_iter_start_indx = find_prev_iterator_start(
#                         sample_tokens, indx_s-1)

#                     if prev_iter_found:

#                         prev_square = sample_tokens[prev_iter_start_indx:indx_s]
#                         square = sample_tokens[indx_s:iter_end_indx+1]

#                         internal_wrapper = roadrunner(
#                             prev_square, square, 0, 0, [])

#                         if internal_wrapper is not None:
#                             wrapper = clean_wrapper_iterators(
#                                 wrapper, smpl_token[1], internal_wrapper)
#                             return roadrunner(wrapper_tokens, sample_tokens, indx_w, iter_end_indx+1, wrapper)

#                         else:
#                             iterative = False

#                     else:
#                         iterative = False

#                 else:
#                     iterative = False
#             else:
#                 iterative = False

#             # check for optional
#             if not iterative:
#                 # option is present on wrapper
#                 if matching_tokens(wrapper_tokens[indx_w+1], smpl_token):
#                     optional = ["optional", " ".join(
#                         ["(", wrap_token[1], ")?"])]
#                     wrapper.append(optional)
#                     return roadrunner(wrapper_tokens, sample_tokens, indx_w+1, indx_s, wrapper)

#                 elif matching_tokens(wrap_token, sample_tokens[indx_s+1]):
#                     optional = ["optional", " ".join(
#                         ["(", smpl_token[1], ")?"])]
#                     wrapper.append(optional)
#                     return roadrunner(wrapper_tokens, sample_tokens, indx_w, indx_s+1, wrapper)
#                 else:
#                     # print(": >>>> ", wrap_token, " vs ", smpl_token)
#                     # print(": >>>> ", wrapper_tokens[indx_w+1], " vs ", smpl_token)
#                     # print(": >>>> ", wrap_token, " vs ", sample_tokens[indx_s+1])
#                     # print("ERROR MATCHING OPTIONAL !!! ")
#                     return None


# def main():
#     """ READ INPUT FILES """
#     wrapper_page = read_html_code('../data/test_pages/wrapper_page.html')
#     sample_page = read_html_code('../data/test_pages/sample_page.html')

#     """ INITIALIZE PARSERS """
#     r_parser = RunnerHTMLParser()

#     """ TOKENIZE HTML PAGES """
#     r_parser.feed(wrapper_page)
#     wrapper_tokens = r_parser.page_tokens
#     # for t in wrapper_tokens:
#     #     print(t)
#     r_parser.clear_page_tokens()

#     r_parser.feed(sample_page)
#     sample_tokens = r_parser.page_tokens
#     # for t in sample_tokens:
#     #     print(t)

#     """ RUN ROADRUNNER """
#     wrapper = roadrunner(wrapper_tokens, sample_tokens, 0, 0, [])

#     ufre = write_final_wrapper_as_ufre(wrapper)
#     print(ufre)


# if __name__ == "__main__":
#     main()
