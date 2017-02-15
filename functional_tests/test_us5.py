from django.urls import reverse

from astorcore.models import ContentPage

from functional_tests.base import FunctionalTest, User


class AddComentsTest(self):

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
        page1 = fly.add_page(ContentPage(**data))
        page1.publish()

        import time; time.wait(1)

        data = dict(
            title="Flies are awesome!", 
            abstract="The past and future of our species.",
            body="If not for spiders, flies would dominated the universe "
                 "a long time ago." 
        ) 
        page2 = fly.add_page(ContentPage(**data))
        page2.publish()

        # Spider vistis fly profile page.
        self.browser.get(reverse("astromain:profile", 
                                  kwargs={"slug": fly.slug}))

        self.wait_for_page_with_text_in_url("da/fly")

        # He can see big heading containing 'Fly'
        heading = self.browser.find_element_by_id("id_profile_heading")
        self.assertContains("Fly", heading)

        # 'It has to be her profile' - he thinks. There are two analyses.
        analyses = self.browser.find_elements_by_class_name("analysis_wrapper") 
        self.assertEqual(len(analyses), 2)

        # The title of first analysis is 'Flies are awesome!'
        title = analyses[0].find_element_by_class_name("analysis_title")
        self.assertEqual(title.text, page2.title)

        # Spider thinks it can be very interesting and clicks the title.
        self.browser.find_element_by_link_text(page2.title).clicks()

        # The page updates and he can see the analysis
        self.wait_for_page_which_url_ends_with("pages/{:d}/".format(page.id))

        title = self.browser.find_element_by_id("id_title")
        self.assertEqual(title.text, page2.title)

        # Spider reads abstract and body
        self.browser.find_element_by_id("id_abstract")
        self.browser.find_element_by_id("id_body")

        # He didn't like the what he had read. He wants to leave a comment.
        # There is comment section but he has to log in to add comments.
        self.browser.find_element_by_id("comments_list")
        self.assertEqual(
            self.browser.find_element_by_id("comments_info").text,
            "Only authenticated users can leave comments. "
            "Please login or register to add comment."
        )

        fly_page_url = self.browser.current_url

        # Spider clicks 'login' and it's being redirect to login page where he
        # enters his username and password.
        self.wait_for_page_which_url_ends_with("account/login/")
        self.login_user(username="Spider", password="spider1")

        # After successful login he is automatically redirected to last page.
        self.assertEqual(self.browser.current_url, fly_page_url)

        # The previous information disappeared and now he can see form to 
        # enter comment.
        inputbox_body = self.browser.find_element_by_class_name("title_input")

        self.fail("finish the test")