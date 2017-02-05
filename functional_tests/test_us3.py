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

        import time; time.sleep(2)

        # Fly was positively authenticated and automatically redirected
        # to her account page.
        self.assertEqual(
            self.browser.current_url,
            os.path.join(self.live_server_url, "account/")
        )

        # She notices information persuading her to create her first entry.
        self.browser.find_element_by_link_text("Create Your First Page")

        # Fly ignores the prompt and clicks "Analyses" from the left sidebar.
        self.browser.find_element_by_link_text("Analyses").click()

        import time; time.sleep(3)

        # Browser shows her root page.
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse("astoraccount:page_edit", 
                kwargs={"page_id": user.root_page.id})
        )

        # The page changes and she sees a link with text 'Add child page' which
        # she clicks.
        self.browser.find_element_by_link_text("Add child page").click()

        # The list with types of pages appears and she select 'Content Page'
        self.browser.find_element_by_link_text("Content Page").click()

        # She fills the forms.
        self.fill_content_page_form(
            title = "Flies are super!",
            abstract = "The past and future of our species.",
            body = "If not for spiders, flies would dominated the universe "
                   "a long time ago."
        )
  
        # She wants to publish her entry but she has still some doubts and
        # needs to check something in external source. She decides to save
        # the draft and publish it later. She clicks 'Save draft'.
        self.browser.find_element_by_xpath(
            "//input[@type='submit' and @value='Save Draft']"
        ).click()

        # After a while information appears that the article has been
        # successfuly saved.
        messages = self.browser.find_element_by_class_name("messages").\
                        find_elements_by_tag_name("li")
        self.assertIn(
            "The draft was saved.",
            [msg.text for msg in messages]
        )

        # She clicks "ASTOR" what redirects her to main page.
        self.browser.find_element_by_link_text("ASTOR").click()