import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest



class NewPageTest(FunctionalTest):

    def test_can_create_new_page(self):
        # Spider is the new user of ASTOR. He has already signed up and has just
        # logged into his account. He visits his account for the first time.
        # self.create_pre_authenticated_session("spider", "spiderpass")
        self.browser.get(self.live_server_url + "/tests/login")

        # Spider opens ASTOR page and clicks "My Astor"
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text("My Astor").click()

        # Spider notices information persuading him to create his first content.
        # That is excacly what he would like to do, so he clicks the link with
        # label: 'Create Your First Page'.
        self.browser.find_element_by_link_text("Create Your First Page").click()

        import time; time.sleep(5)

        # The page updates and he is asked for choosing the type of the page. He
        # has two choices: 'Content Page', 'Index Page'. There is also short
        # explanating but he is too lazy to read it. 
        content_page = self.browser.find_element_by_link_text("Content Page")
        index_page = self.browser.find_element_by_link_text("Index Page")

        # Spider chooses 'Content Page' and he is redirected to 'Editor' where 
        # he has to input content of his new page. 
        content_page.click()

        # He spots input box where he enters the title: "Test Artice"
        inputbox_title = self.browser.find_element_by_id("id_title")
        self.assertEqual(
            inputbox_title.get_attribute("placeholder"),
            "Enter a title."
        )
        
        # He types'Test Article' into a text box and presses enter.
        inputbox_title.send_keys("Test Article")
        inputbox_title.send_keys(Keys.ENTER)

        # When he presed Enter, he was switch to next inputbox.
        inputbox_abstract = self.browser.switch_to.active_element["value"]
        self.assertEqual(inputbox_abstract.get_attribute("id"), 
                         "id_abstract")

        # He writes in Absract: "Testing ASTOR. How to create new page with 
        # content" and presses enter.
        inputbox_abstract.send_keys("Testing ASTOR. How to create new page "
                                    "with content.")

        # He moves to body section where he can enter the proper content of
        # his new page. 
        inputbox_body = self.browser.find_element_by_id("id_body")
        inputbox_body.send_keys("Testing. I will put here more later.")   

        # After filling all fields he clicks 'Publish' button.
        self.browser.find_element_by_xpath(
            "//input[@type='submit' and @value='Publish']"
        ).click()

        # After a while information appears that the article has been
        # successfuly published.
        messages = self.browser.find_element_by_class_name("messages").\
                        find_elements_by_tag_name("li")
        self.assertIn(
            "The page was updated and published successfully.",
            [msg.text for msg in messages]
        )

        # Spider is very proud of himself for creating new page and clicks
        # link with 'My Astor' text to return to main page of his profile.
        self.browser.find_element_by_link_text("My Astor").click()
        self.browser.implicitly_wait(5)

        # The page changes and he sees new entry in his latest activity section.
        # It says: "New article published on <date>"
        acts_list = self.browser.find_element_by_id("id_list_activities")
        acts = acts_list.find_elements_by_tag_name("li")
        self.assertTrue(any("Page updated" in act.text for act in acts))

        # Spider clicks "Log out" and close the browser.
        self.browser.find_element_by_link_text("Log Out").click()