import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest


@unittest.skip
class FunctionalTestTest(FunctionalTest):

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.live_server_url)
        self.assertIn("ASTOR", self.browser.title)
        self.fail("Finish the test!")


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

        # The page updates and he is asked for choosing the type of the page. He
        # has two choices: 'Content Page', 'Index Page'. There is also short
        # explanating but he is too lazy to read it. 
        content_page = self.browser.find_element_by_link_text("Content Page")
        index_page = self.browser.find_element_by_link_text("Index Page")

        # Spider chooses 'Content Page' and he is redirected to 'Editor' where 
        # he has to input content of his new page. 
        content_page.click()

        # He spots input box where he enters the title: "Test Artice"
        inputbox_title = self.browser.find_element_by_id("id-new-title")
        self.assertEqual(
            inputbox_title.get_attribute("placeholder"),
            "Enter a title"
        )
        
        # He types'Test Article' into a text box and presses enter.
        inputbox_title.send_keys("Test Article")
        inputbox_title.send_keys(Keys.ENTER)

        # When he presed Enter, he was shifted toward next inputbox.
        inputbox_abstract = self.browser.switchTo().activeElement()
        self.assertEqual(inputbox_abstract.get_attribute("id"), 
                         "id-new-abstract")

        # He writes in Absract: "Testing ASTOR. How to create new page with 
        # content" and presses enter.
        inputbox_abstract.send_keys("Testing ASTOR. How to create new page"
                                    "with content.")
        inputbox_title.send_keys(Keys.ENTER)

        # He moves to body section where he can enter the proper content of
        # his new page. 
        inputbox_body = self.browser.switchTo().activeElement()
        self.assertEqual(inputbox_abstract.get_attribute("id"), 
                         "id-new-body")

        inputbox_body.send_keys("Testing. I will put here more later.")   

        # After filling all fields he clicks 'Publish' button.
        self.browser.find_element_by_link_text("Publish").click()

        # After a while information appears that the article has been
        # successfuly published.
        self.browser.implicitly_wait(3)
        self.browser.find_elements_by_xpath(
            "//*[contains(text(), 'Published on')]"
        )

        # Spider is very proud of himself for creating new page and clicks
        # link with 'My Astor' text to return to main page of his profile.
        self.browser.find_element_by_link_text("My Astor").click()

        # The page changes and he sees new entry in his latest activity section.
        # It says: "New article published on <date>"
        act_list = self.browser.find_element_by_id("id_list_activities")
        acts = activities.find_elements_by_tag_name("li")
        self.assertIn(
            "New article published on",
            [act.text for act in acts]
        )

        # Spider clicks "Log out" and close the browser.
        self.browser.find_element_by_link_text("Log out").click()