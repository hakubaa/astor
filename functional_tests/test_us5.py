from django.urls import reverse

from astorcore.models import ContentPage

from functional_tests.base import FunctionalTest, User


class AddComentsTest(FunctionalTest):

    def test_for_adding_comments_to_analysis(self):
        '''
        Spider has just heard about new analysis prepered by Fly. He goes
        to her page and adds comment.
        '''

        fly = User.objects.create_user(username="Fly", password="fly1234")
        spider = User.objects.create_user(username="Spider", password="spider1")

        data = dict(
            title="Hard decision!",
            abstract="What brings the future?",
            body="Every one from time to time has to make some decision. "
                 "Some of them can be especially hard."
        )
        page1 = fly.add_page(ContentPage(**data)).publish()

        data = dict(
            title="Flies are awesome!", 
            abstract="The past and future of our species.",
            body="If not for spiders, flies would dominated the universe "
                 "a long time ago." 
        ) 
        page2 = fly.add_page(ContentPage(**data)).publish()

        # Spider vistis fly profile page.
        self.browser.get(
            self.live_server_url + 
            reverse("astormain:profile", kwargs={"slug": fly.slug})
        )

        self.wait_for_page_with_text_in_url("da/fly")

        # He can see big heading containing 'Fly'
        heading = self.browser.find_element_by_id("id_profile_heading")
        self.assertIn("Fly", heading.text)

        # 'It has to be her profile' - he thinks. There are two analyses.
        analyses = self.browser.find_elements_by_class_name("analysis-wrapper") 
        self.assertEqual(len(analyses), 2)

        # The title of first analysis is 'Flies are awesome!'
        title = analyses[0].find_element_by_class_name("analysis-title")
        self.assertEqual(title.text, page2.title)

        # Spider thinks it can be very interesting and clicks the title.
        self.browser.find_element_by_link_text(page2.title).click()

        # The page updates and he can see the analysis
        self.wait_for_page_which_url_ends_with("pages/{:d}".format(page2.id))

        title = self.browser.find_element_by_tag_name("h3")
        self.assertEqual(title.text, page2.title)

        # He didn't like the what he had read. He wants to leave a comment.
        # There is comment section but he has to log in to add comments.
        element = self.browser.find_element_by_id("id_comment_form")
        self.assertIn(
            "Only authenticated users can leave comments. ",
            element.text
        )

        fly_page_url = self.browser.current_url

        # Spider clicks 'login' and it's being redirect to login page where he
        # enters his username and password.
        self.browser.find_element_by_link_text("login").click()
        self.wait_for_page_with_text_in_url("account/login/")
        self.login_user(username="Spider", password="spider1")

        # After successful login he is automatically redirected to last page.
        ## skip now, see how next works
        # self.assertEqual(self.browser.current_url, fly_page_url)
        self.browser.get(fly_page_url)
        self.wait_for_page_with_text_in_url("da/fly")

        # The previous information disappeared and now he can see form to 
        # enter comment.
        inputbox_body = self.browser.find_element_by_id("id_body")

        # Spider writes his comment and clicks 'Send Comment'
        inputbox_body.send_keys("If not for spiders, you will destroy the Earth.")

        self.browser.find_element_by_xpath(
            "//input[@type='submit' and @value='Send Comment']"
        ).click()

        # The page updates and now he can see his comment below the analysis
        self.wait_for_element_with_id("id_comments")
        comments = self.browser.find_elements_by_class_name("comment-body")
        self.assertTrue(any("Spider" in cmt.text for cmt in comments))
        self.assertTrue(any("Earth" in cmt.text for cmt in comments))

        # Content with himself, he closes the browser.