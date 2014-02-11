import json
import os
import sys

try:
    from unittest import TestCase, mock
except ImportError:
    import mock
    from unittest import TestCase


from cepko import Cepko

sys.path.insert(0, os.path.abspath('..'))

BIG_DICT = {
    "cpu": 1000,
    "cpus_instead_of_cores": False,
    "global_context": {"some_global_key": "some_global_val"},
    "mem": 1073741824,
    "meta": {"ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2E.../hQ5D5 john@doe"},
    "name": "test_server",
    "requirements": [],
    "smp": 1,
    "tags": ["much server", "very performance"],
    "uuid": "65b2fb23-8c03-4187-a3ba-8b7c919e8890",
    "vnc_password": "9e84d6cb49e46379"
}


@mock.patch("cepko.CepkoResult._execute", lambda *args: "")
class CepkoRequestsTests(TestCase):
    def setUp(self):
        self.c = Cepko()

    def test_all(self):
        self.assertEqual("<\n\n>", self.c.all().request)
        self.assertEqual("<\n\n>", self.c.get().request)

    def test_get_single_key(self):
        self.assertEqual("<\nname\n>", self.c.get("name").request)
        self.assertEqual("<\n/name\n>", self.c.get("/name").request)

    def test_get_nested_key(self):
        self.assertEqual("<\nmeta/ssh_public_key\n>", self.c.get("meta/ssh_public_key").request)
        self.assertEqual("<\n/tags/0\n>", self.c.get("/tags/0").request)

    def test_meta(self):
        self.assertEqual("<\n/meta/\n>", self.c.meta().request)
        self.assertEqual("<\n/meta/public_ssh_key\n>", self.c.meta("public_ssh_key").request)

    def test_global_context(self):
        self.assertEqual("<\n/global_context/\n>", self.c.global_context().request)
        self.assertEqual("<\n/global_context/public_ssh_key\n>", self.c.global_context("public_ssh_key").request)


class CepkoResultTests(TestCase):
    def setUp(self):
        self.c = Cepko()

    @mock.patch("cepko.CepkoResult._execute", lambda *args: json.dumps(BIG_DICT))
    def test_getitem(self):
        result = self.c.all()
        self.assertEqual("65b2fb23-8c03-4187-a3ba-8b7c919e8890", result['uuid'])
        self.assertEqual([], result['requirements'])
        self.assertEqual("much server", result['tags'][0])
        self.assertEqual(1, result['smp'])

    @mock.patch("cepko.CepkoResult._execute", lambda *args: json.dumps(BIG_DICT))
    def test_len(self):
        self.assertEqual(len(BIG_DICT), len(self.c.all()))

    @mock.patch("cepko.CepkoResult._execute", lambda *args: json.dumps(BIG_DICT))
    def test_contains(self):
        result = self.c.all()
        self.assertTrue('uuid' in result)
        self.assertFalse('uid' in result)
        self.assertTrue('meta' in result)
        self.assertFalse('ssh_public_key' in result)

    @mock.patch("cepko.CepkoResult._execute", lambda *args: json.dumps(BIG_DICT))
    def test_iter(self):
        self.assertEqual(sorted(BIG_DICT.keys()), sorted([key for key in self.c.all()]))

    @mock.patch("cepko.CepkoResult._execute", lambda *args: json.dumps(BIG_DICT['tags']))
    def test_with_list_as_result(self):
        result = self.c.all()
        self.assertEqual('much server', result[0])
        self.assertTrue('very performance' in result)
        self.assertEqual(2, len(result))
