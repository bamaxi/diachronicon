import unittest

from config import TestConfig
from app import create_app


SEARCH_PARAM2RESULTS = {
    'c-id': [
        (1, 'N-Gen.Pl Cop (хоть) пруд пруди'),
        (19, "Prep N-Dat.Sg не по адресу"),
        (21, "в точности PronDem"),
        (22, "NumCrd N с гаком"),
        (23, "NP Cop не что (иное) как NP"),
        (24, "NP-Gen не*густо"),
        (25, "(NP) все до одного (NP-Gen)"),
        (2023, "ни капли N-Gen"),
        (2024, "ни капли не VP"),
        (2025, "(у NP-Gen) руки не доходят / дойдут / дошли / дойдут (Inf / до NP-Gen)"),
        (2026, "на кой NP-Nom (NP-Dat) сдаться-Pst"),
        (2027, "NP-Dat Cop до лампочки (NP-Nom)"),
        (2032, "не ахти ((PronInt) NP) / не ахти ((PronInt) AdvP)"),
        (2033, "((N-Nom) Cop) без понятия"),
        (2034, "N-Nom знает ((PronInt) (NP))"),
        (2035, "Фиг NP-Dat"),
        (2036, "(N-Nom) ни рыба ни мясо"),
        (2037, "(у NP-Gen | в NP-Loc | не Cop) ни стыда ни совести"),
        (2039, "V-Pst"),
        (20310, "айда VP"),
        (20313, "Cop без царя в голове"),
        (20315, "NP XP ни-ни!"),
        (20316, "не то чтобы XP ((CCONJ) XP)"),
    ],
    'c-formula': [
        ("dat", "Prep N-Dat.Sg не по адресу"),
        ("dat", "на кой NP-Nom (NP-Dat) сдаться-Pst"),
        ("dat", "NP-Dat Cop до лампочки (NP-Nom)"),
        ("dat", "Фиг NP-Dat"),

        ("pst", "на кой NP-Nom (NP-Dat) сдаться-Pst"),
        ("pst", "V-Pst"),

        # ("")
    ],
    'c-meaning': [
        ("Causation", "V-Pst"),
        ("Causation", "айда VP"),
    ],
    # 'c-name': [
    #     ("пруд пруди", "N-Gen.Pl Cop (хоть) пруд пруди"),
    #     ("не по адресу", "Prep N-Dat.Sg не по адресу"),
    #     ("в точности", "в точности PronDem"),
    #     ("с гаком", "NumCrd N с гаком"),
    #     ("не что (иное) как", "NP Cop не что (иное) как NP"),
    #     ("не*густо", "NP-Gen не*густо"),
    #     ("все до одного / все до единого", "(NP) все до одного (NP-Gen)"),
    #     ("ни капли1", "ни капли N-Gen"),
    #     ("ни капли2", "ни капли не VP"),
    #     ("руки не доходят", "(у NP-Gen) руки не доходят / дойдут / дошли / дойдут (Inf / до NP-Gen)"),
    #     ("на кой сдался", "на кой NP-Nom (NP-Dat) сдаться-Pst"),
    #     ("до лампочки", "NP-Dat Cop до лампочки (NP-Nom)"),
    #     ("не ахти", "не ахти ((PronInt) NP) / не ахти ((PronInt) AdvP)"),
    #     ("без понятия", "((N-Nom) Cop) без понятия"),
    #     ("черт знает", "N-Nom знает ((PronInt) (NP))"),
    #     ("фиг тебе", "Фиг NP-Dat"),
    #     ("ни рыба ни мясо", "(N-Nom) ни рыба ни мясо"),
    #     ("ни стыда ни совести", "(у NP-Gen | в NP-Loc | не Cop) ни стыда ни совести"),
    #     ("прошедшее время в значении побуждения {встал!, сел!}", "V-Pst"),
    #     ("глагольные конструкции с частицей «айда» {айда купаться!, айда погреемся!}", "айда VP"),
    #     ("без царя в голове", "Cop без царя в голове"),
    #     ("ни-ни", "NP XP ни-ни!"),
    #     ("не то чтобы", "не то чтобы XP ((CCONJ) XP)"),
    # ]
    'c-synt_function_of_anchor': [
        ("Praedicative Expression", "N-Gen.Pl Cop (хоть) пруд пруди"),
        ("Praedicative Expression", "Prep N-Dat.Sg не по адресу"),
        ("Praedicative Expression", "NP-Dat Cop до лампочки (NP-Nom)"),
        ("Praedicative Expression", "Фиг NP-Dat"),
        ("Praedicative Expression", "(N-Nom) ни рыба ни мясо"),
        ("Praedicative Expression", "(у NP-Gen | в NP-Loc | не Cop) ни стыда ни совести"),
        ("Praedicative Expression", "Cop без царя в голове"),
        ("Praedicative Expression", "NP XP ни-ни!"),
    ]
}


class DBSearchTestCase(unittest.TestCase):
    def test_duration_like(self): ...
        # TODO:
        # session.execute(select(Change).where(
        #    Change.last_attested - Change.first_attested >= 100)
        # ).scalars().all()


class AppFactoryTestCase(unittest.TestCase):
    def test_factory(self):
        assert not create_app().testing

        test_config = TestConfig()
        test_config.TESTING = True
        assert create_app(test_config).testing


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app(test_config_obj=TestConfig)#, remove_wsgi_logger=True)
        self.app = app
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    # def test_home(self):
    #     response = self.client.post("/", data={"content": "hello world"})
    #     assert response.status_code == 200
    #     assert "POST method called" == response.get_data(as_text=True)

    def get_route(self, link, *args, **kwargs):
        response = self.client.get(link, *args, **kwargs)
        return response, response.status_code

    def test_main(self):
        response, status_code = self.get_route('/')
        assert status_code == 200

    def test_search_loads(self):
        response, status_code = self.get_route('/search/')
        assert status_code == 200

    def test_simple_search_404(self):
        response, status_code = self.get_route('/simple-search/')
        assert status_code == 404

    def get_construction_page(self, id_):
        link_template = "/construction/{}/"
        return self.get_route(link_template.format(id_))

    def test_construction_pages(self):
        construction_ids = (
            1, 19, 21, 22, 23, 24, 25,
            2023, 2024, 2025, 2026, 2027,
            2032, 2033, 2034, 2035, 2036, 2037, 2039, 20310, 20313, 20315, 20316)

        for id_ in construction_ids:
            with self.subTest(construction_id=id_):
                response, status_code = self.get_construction_page(id_)
                assert status_code == 200

    @unittest.skip
    def test_search_content(self):
        for param, val_res_list in SEARCH_PARAM2RESULTS.items():
            for val, res in val_res_list:
                with self.subTest(parameter=param, value=val, result=res):
                    response, status_code = self.get_route(
                        '/search/', query_string={param: val}
                    )

                    assert status_code == 200, "failed to perform search with parameters"

                    response_text = response.get_data(as_text=True)

                    # print(response_text)
                    assert res in response_text, "expected result is not in response text"


class TestContent(unittest.TestCase):
    pass


if __name__ == "__main__":
    # test_construction_pages()
    # test_page_loads('http://127.0.0.1/search', "plain search page")
    unittest.main()

