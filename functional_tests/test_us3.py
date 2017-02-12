import os

from django.urls import reverse
from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest


class CreatingDraftsTest(FunctionalTest):

    def fill_content_page_form(self, title, abstract="", body=""):
        inputbox_title = self.browser.find_element_by_id("id_title")
        inputbox_title.send_keys(title)
        inputbox_abstract = self.browser.find_element_by_id("id_abstract")
        inputbox_abstract.send_keys(abstract)
        if body:
            inputbox_body = self.browser.find_element_by_id("id_body")
            inputbox_body.send_keys(body) 


    def test_create_and_edit_drafts(self):
        # Fly created account on ASTOR yesterday. Today she is going to 
        # create her first entry. 
        user = self.create_user(username="Fly", password="abcd")

        #She visits ASTOR home page.
        self.browser.get(self.live_server_url)

        # She clicks Login link.
        self.browser.find_element_by_link_text("Log In").click()

        # Login form appears.
        username = self.browser.find_element_by_id("id_username")
        password = self.browser.find_element_by_id("id_password")

        # Fly enters her username.
        username.send_keys(user.username)

        # She presses Enter what switch her to next input.
        username.send_keys(Keys.ENTER)

        inputbox = self.browser.switch_to.active_element["value"] 
        self.assertEqual(inputbox.get_attribute("id"),  "id_password") 

        # She enters her password and presses Enter.
        password.send_keys("abcd")
        password.send_keys(Keys.ENTER)

        # Fly was positively authenticated and automatically redirected
        # to her account page.
        self.wait_for_page_which_url_ends_with("account/")

        # She notices information persuading her to create her first entry.
        self.browser.find_element_by_link_text("Create Your First Page")

        # Fly ignores the prompt and clicks "Analyses" from the left sidebar.
        self.browser.find_element_by_link_text("Analyses").click()

        # The page changes and she sees a link with text 'Add child page' which
        # she clicks.
        self.wait_for_page_which_url_ends_with("account/analyses/")
        self.browser.find_element_by_link_text("Add New Analysis").click()

        # The list with types of pages appears and she select 'Content Page'
        self.browser.find_element_by_link_text("Content Page").click()

        import time; time.sleep(1)

        # She fills the forms.
        self.wait_for_element_with_id("id_title", timeout=15)
        page_url = self.browser.current_url
        self.fill_content_page_form(
            title = "Flies are super!",
            abstract = "The past and future of our species."
            #body = "If not for spiders, flies would dominated the universe "
            #       "a long time ago."
        )
  
        # She wants to publish her entry but she has still some doubts and
        # needs to check something in external source. She decides to save
        # the draft and publish it later. She clicks 'Save draft'.
        self.browser.find_element_by_xpath(
            "//button[@type='submit' and @value='save_draft']"
        ).click()

        # After a while information appears that the article has been
        # successfuly saved.
        self.check_for_message("The draft has been saved.")

        # She clicks "ASTOR" what redirects her to main page.
        self.browser.find_element_by_link_text("ASTOR").click()
        self.wait_for_page_which_url_ends_with(self.live_server_url + "/")

        # Fly cannot see her analysis in section with latest entries
        self.check_for_entry_in_newest_section(
            "Flies are super!", assert_true=False
        )

        # She decides to publish her fantastic article. Se clisk 'My Astor'
        self.browser.find_element_by_link_text("My Astor").click()
        self.wait_for_page_which_url_ends_with("account/")

        # The page updates and she can see in section with the latest
        # updates that she was working on page with title 'Flies are super!'
        self.browser.find_element_by_id("id_recent_edits")
        self.check_for_edit_in_recent_section("Flies are super!")

        # She clicks the title of the entry what redirects her to page where
        # she can edit the content.
        self.browser.find_element_by_link_text("Flies are super!").click()
        self.wait_for(lambda: page_url == self.browser.current_url)

        # Fly updates the title
        input_title = self.browser.find_element_by_id("id_title")
        input_title.clear()
        input_title.send_keys("Flies are awesome!")

        # And she clicks Publish.
        self.browser.find_element_by_xpath(
            "//button[@type='submit' and @value='publish']"
        ).click()

        # After a while information appears that the article has been
        # successfuly saved.
        self.check_for_message("The analysis has been saved and published.")

        # She clicks "ASTOR".
        self.browser.find_element_by_link_text("ASTOR").click()
        self.wait_for_page_which_url_ends_with(self.live_server_url + "/")

        # She can see now that her entry is on the main page <jupi>.
        self.check_for_entry_in_newest_section("Flies are awesome!")

        # Very proud of herself, she clicks "Log Out"
        self.browser.find_element_by_link_text("Log Out").click()