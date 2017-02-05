from astorcore.models import ContentPage, Page
from astoraccount.models import User

from functional_tests.base import FunctionalTest


class ReadingEntriesTest(FunctionalTest):

    def find_section_with_the_newest_entries(self):
        return self.browser.find_element_by_id("id_newest_entries")

    def check_for_entry_in_newest_section(self, title):
        section = self.find_section_with_the_newest_entries()
        entries = section.find_elements_by_tag_name("li")
        self.assertTrue(any(title in entry.text for entry in entries))

    def test_can_read_entries_of_other_user(self):
        # Spider told her favourite firend Fly about the new website he had 
        # discovered and his first publication.

        user = User.objects.create_user(username="Spider", password="spider")
        page = ContentPage(title="Spiders eat flies", 
                           abstract="Short dispute over importance of proper eating.",
                           body="For the generations, our ancestors hunted (...)")
        user.add_page(page)
        page.publish()

        # Fly visits ASTOR webpage.
        self.browser.get(self.live_server_url)

        # That is not the prettiest webpage she had ever seen, but it's very
        # readable and easy to navigate. She spots the section 'Newest Entries'.
        section = self.find_section_with_the_newest_entries()

        # To her suprise the first entry has the same title as Spider's article.
        # 'It has to be it' - she thinks. 
        self.check_for_entry_in_newest_section(page.title)

        # She clicks the title.
        entry = self.browser.find_element_by_link_text(page.title)
        entry.click()

        # The page updates and she can see a header at the top of page with 
        # the title.
        title = self.browser.find_element_by_id("id_page_title")
        self.assertEqual(title.text, page.title)

        # There is also short abstract
        abstract = self.browser.find_element_by_id("id_page_abstract")
        self.assertEqual(abstract.text, page.abstract)

        # And the content of the article
        body = self.browser.find_element_by_id("id_page_body")
        self.assertEqual(body.text, page.body)

        user = User.objects.create_user(username="SuperFly", password="fly")
        page = ContentPage(
            title="The superiority of flies over spiders", 
            abstract="Who can fly, can reach the sky",
            body="Flies can fly, Flies can walk, spiders are stupid (...)"
        )
        user.add_page(page)
        page.publish()

        # Fly reads all of the infromation, and becomes a little bit worry of
        # Spider and his intentation. "Can it be a trap?" - she thinks. She
        # immedietaly clicks "ASTOR" link which redirects her to main page.
        self.browser.find_element_by_link_text("ASTOR").click()

        # Main page change a little bit and there is one more entry in the 
        # newest section.
        section = self.find_section_with_the_newest_entries()
        entries = section.find_elements_by_tag_name("li")
        self.assertEqual(len(entries), 2)

        # Thre is a new entry at the top with ttitle: "The superiority of flies 
        # over spiders"
        self.check_for_entry_in_newest_section(
            "The superiority of flies over spiders"
        )

        # The entry was published by 'SuperFly'.
        authors = self.browser.find_elements_by_class_name("entry_author")
        self.assertIn("SuperFly", [item.text for item in authors])

        # Fly decides to read this entry next day, and to creat her own account 
        # and start publishing her own thoughts. Now she closes the browser.