from django.urls import reverse
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from astorcore.models import ContentPage

from functional_tests.base import FunctionalTest, User



class AddTagsTest(FunctionalTest):

    # def setUp(self):
    #     self.browser = webdriver.Chrome()
    #     self.browser.implicitly_wait(3)

    def find_analysis_with_title(self, title):
        analyses = self.browser.find_elements_by_class_name("analysis")
        for analysis in analyses:
            tds = analysis.find_elements_by_tag_name("td")
            if any(title in td.text for td in tds):
                return analysis
        return None

    def assert_tags(self, tags):
        tags_live = self.find_tags()
        tags_live = [ tag.text for tag in tags_live ]
        self.assertTrue(all(tag in tags_live for tag in tags))

    def find_tags(self):
        tags_container = self.browser.find_element_by_id("id_tags")
        tags = tags_container.find_elements_by_tag_name("li")
        return tags

    def test_can_add_tags(self):
        '''
        Fly has just been told by Spider that she can add tags to her analyses 
        what enable to group them and make them easier searchable.
        '''
        
        user = User.objects.create_user(username="Fly", password="fly1234")
        data = dict(
            title="Flies are awesome!", 
            abstract="The past and future of our species.",
            body="If not for spiders, flies would dominated the universe "
                 "a long time ago." 
        ) 
        page = user.add_page(ContentPage(**data))
        page.publish()

        # Fly visits her latest favourite page ASTOR and logs into her account.
        self.browser.get(self.live_server_url)
        self.login_user(username="Fly", password="fly1234")

        self.wait_for_page_which_url_ends_with("/account/")

        # She is already very familier with the structue of the main panel and
        # immedietaly clicks 'Analyses' from the left sidebar.
        self.browser.find_element_by_link_text("Analyses").click()

        self.wait_for_page_which_url_ends_with("/account/analyses/")

        # Fly sees list of her analyses. There is only one now, but she can 
        # always create new one with big green button 'Add New Analysis'
        self.browser.find_element_by_link_text("Add New Analysis")

        self.assertEqual(
            len(self.browser.find_elements_by_class_name("analysis")), 1
        )

        # She can see that her analysis is 'LIVE'. There is a status which 
        # say this.
        analysis = self.find_analysis_with_title(data["title"])
        self.assertIsNotNone(analysis)

        tds = analysis.find_elements_by_tag_name("td")
        self.assertTrue(any("LIVE" in td.text for td in tds))

        ## Remember befor switching to new window/tab.
        window_account = self.browser.window_handles[0]

        # It turns out that 'LIVE' is a button, so she clicks it.
        self.browser.find_element_by_link_text("LIVE").click()

        # The new page opens and there is her article. WOW
        self.assertEqual(len(self.browser.window_handles), 2)
        self.browser.switch_to_window(self.browser.window_handles[1])
        self.wait_for_page_with_text_in_url("da/fly")

        abstract = self.browser.find_element_by_id("id_abstract")
        self.assertEqual(data["abstract"], abstract.text)

        analysis_url = self.browser.current_url

        # She closes the window and goes back to her account page.
        self.browser.close()
        self.browser.switch_to_window(window_account)

        # Time to add some tags. Fly clicks edit button below the title of 
        # her analysis.
        analysis.find_element_by_link_text("Edit").click()

        # The page changes to one with analysis editor. 
        # 'I love this editor' - she thinks.
        self.wait_for_element_with_id("id_title")

        # There are three tabs, and she switches to ''. 
        self.browser.find_element_by_link_text("Promote").click()

        # Fly spots input box for tags. There she has to put tags she 
        # wants to ascribe to this analysis.
        inputbox_tags = self.browser.find_element_by_id("id_tags")

        ## Make input box visible (otherwise error: Element is not visible)
        self.browser.execute_script(
            "document.getElementById('id_tags').style.display='inline';"
        )
        import time; time.sleep(1)

        # She enters names of three tags.
        inputbox_tags.send_keys("flies, spiders, flying")

        # And then clicks 'Save & Publish' button.
        self.browser.find_element_by_xpath( 
             "//button[@type='submit' and @value='publish']" 
        ).click() 

        # Message appears which confirms successful save & publish of analysis.
        self.check_for_message("The analysis has been saved and published.") 

        # Fly wants to see whether the tags can be see in the 'live' version 
        # of her analysis. She memorized the url of the page and go there 
        # straight away.
        self.browser.get(analysis_url)

        self.wait_for_page_with_text_in_url("da/fly")

        # Now she can see below the title three words.
        tags = self.find_tags()
        self.assertEqual(len(tags), 3)
        self.assert_tags(["flies", "spiders", "flying"])

        # That my tags. Content with herself she closes the browser.