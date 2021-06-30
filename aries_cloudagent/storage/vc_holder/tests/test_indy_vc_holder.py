import pytest


from ....config.injection_context import InjectionContext
from ....indy.sdk.profile import IndySdkProfileManager
from ....ledger.indy import IndySdkLedgerPool
from ....wallet.indy import IndySdkWallet

from ..base import VCHolder
from ..vc_record import VCRecord

from . import test_in_memory_vc_holder as in_memory


VC_CONTEXT = "https://www.w3.org/2018/credentials/v1"
VC_TYPE = "https://www.w3.org/2018/credentials#VerifiableCredential"
VC_SUBJECT_ID = "did:example:ebfeb1f712ebc6f1c276e12ec21"
VC_PROOF_TYPE = "Ed25519Signature2018"
VC_ISSUER_ID = "https://example.edu/issuers/14"
VC_SCHEMA_ID = "https://example.org/examples/degree.json"
VC_GIVEN_ID = "http://example.edu/credentials/3732"


async def make_profile():
    key = await IndySdkWallet.generate_wallet_key()
    context = InjectionContext()
    context.injector.bind_instance(IndySdkLedgerPool, IndySdkLedgerPool("name"))
    return await IndySdkProfileManager().provision(
        context,
        {
            "auto_recreate": True,
            "auto_remove": True,
            "name": "test-wallet",
            "key": key,
            "key_derivation_method": "RAW",  # much slower tests with argon-hashed keys
        },
    )


@pytest.fixture()
async def holder():
    profile = await make_profile()
    async with profile.session() as session:
        yield session.inject(VCHolder)
    await profile.close()


def test_record() -> VCRecord:
    return VCRecord(
        contexts=[
            VC_CONTEXT,
            "https://www.w3.org/2018/credentials/examples/v1",
        ],
        expanded_types=[
            VC_TYPE,
            "https://example.org/examples#UniversityDegreeCredential",
        ],
        schema_ids=[VC_SCHEMA_ID],
        issuer_id=VC_ISSUER_ID,
        subject_ids=[VC_SUBJECT_ID],
        proof_types=[VC_PROOF_TYPE],
        given_id=VC_GIVEN_ID,
        cred_tags={"tag": "value"},
        cred_value={
            "@context": [
                VC_CONTEXT,
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            "id": VC_GIVEN_ID,
            "type": ["VerifiableCredential", "UniversityDegreeCredential"],
            "issuer": VC_ISSUER_ID,
            "identifier": "83627467",
            "name": "University Degree",
            "issuanceDate": "2010-01-01T19:53:24Z",
            "credentialSubject": {
                "id": VC_SUBJECT_ID,
                "givenName": "Cai",
                "familyName": "Leblanc",
            },
            "proof": {
                "type": "Ed25519Signature2018",
                "verificationMethod": "did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL",
                "created": "2021-05-07T08:50:17.626625",
                "proofPurpose": "assertionMethod",
                "jws": "eyJhbGciOiAiRWREU0EiLCAiYjY0IjogZmFsc2UsICJjcml0IjogWyJiNjQiXX0..rubQvgig7cN-F6cYn_AJF1BCSaMpkoR517Ot_4pqwdJnQ-JwKXq6d6cNos5JR73E9WkwYISXapY0fYTIG9-fBA",
            },
        },
    )


@pytest.mark.indy
class TestIndySdkVCHolder(in_memory.TestInMemoryVCHolder):
    # run same test suite with different holder fixture

    @pytest.mark.asyncio
    async def test_handle_parser_error(self, holder: VCHolder):
        record = VCRecord(
            contexts=[
                VC_CONTEXT,
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            expanded_types=[
                VC_TYPE,
                "https://example.org/examples#UniversityDegreeCredential",
            ],
            schema_ids=[VC_SCHEMA_ID],
            issuer_id=VC_ISSUER_ID,
            subject_ids=[VC_SUBJECT_ID],
            proof_types=[VC_PROOF_TYPE],
            given_id=VC_GIVEN_ID,
            cred_tags={"tag": "value"},
            cred_value={
                "@context": [
                    VC_CONTEXT,
                    "https://www.w3.org/2018/credentials/examples/v1",
                ],
                "id": VC_GIVEN_ID,
                "type": ["VerifiableCredential", "UniversityDegreeCredential"],
                "issuer": VC_ISSUER_ID,
                "identifier": "83627467",
                "name": "University Degree",
                "issuanceDate": "20180-10-29T21:02:19.201+0000",
                "credentialSubject": {
                    "id": VC_SUBJECT_ID,
                    "givenName": "Cai",
                    "familyName": "Leblanc",
                },
                "proof": {
                    "type": "Ed25519Signature2018",
                    "verificationMethod": "did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL",
                    "created": "2021-05-07T08:50:17.626625",
                    "proofPurpose": "assertionMethod",
                    "jws": "eyJhbGciOiAiRWREU0EiLCAiYjY0IjogZmFsc2UsICJjcml0IjogWyJiNjQiXX0..rubQvgig7cN-F6cYn_AJF1BCSaMpkoR517Ot_4pqwdJnQ-JwKXq6d6cNos5JR73E9WkwYISXapY0fYTIG9-fBA",
                },
            },
        )
        await holder.store_credential(record)
        search = holder.search_credentials()
        rows = await search.fetch()
        assert rows == [record]

    @pytest.mark.asyncio
    async def test_sorting_vcrecord(self, holder: VCHolder):
        record_a = VCRecord(
            contexts=[
                VC_CONTEXT,
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            expanded_types=[
                VC_TYPE,
                "https://example.org/examples#UniversityDegreeCredential",
            ],
            schema_ids=[VC_SCHEMA_ID],
            issuer_id=VC_ISSUER_ID,
            subject_ids=[VC_SUBJECT_ID],
            proof_types=[VC_PROOF_TYPE],
            given_id=VC_GIVEN_ID,
            cred_tags={"tag": "value"},
            cred_value={
                "@context": [
                    VC_CONTEXT,
                    "https://www.w3.org/2018/credentials/examples/v1",
                ],
                "id": VC_GIVEN_ID,
                "type": ["VerifiableCredential", "UniversityDegreeCredential"],
                "issuer": VC_ISSUER_ID,
                "identifier": "83627467",
                "name": "University Degree",
                "issuanceDate": "2010-01-01T19:53:24Z",
                "credentialSubject": {
                    "id": VC_SUBJECT_ID,
                    "givenName": "Cai",
                    "familyName": "Leblanc",
                },
                "proof": {
                    "type": "Ed25519Signature2018",
                    "verificationMethod": "did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL",
                    "created": "2021-05-07T08:50:17.626625",
                    "proofPurpose": "assertionMethod",
                    "jws": "eyJhbGciOiAiRWREU0EiLCAiYjY0IjogZmFsc2UsICJjcml0IjogWyJiNjQiXX0..rubQvgig7cN-F6cYn_AJF1BCSaMpkoR517Ot_4pqwdJnQ-JwKXq6d6cNos5JR73E9WkwYISXapY0fYTIG9-fBA",
                },
            },
        )
        await holder.store_credential(record_a)
        record_b = VCRecord(
            contexts=[
                VC_CONTEXT,
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            expanded_types=[
                VC_TYPE,
                "https://example.org/examples#UniversityDegreeCredential",
            ],
            schema_ids=[VC_SCHEMA_ID],
            issuer_id=VC_ISSUER_ID,
            subject_ids=[VC_SUBJECT_ID],
            proof_types=[VC_PROOF_TYPE],
            given_id=VC_GIVEN_ID,
            cred_tags={"tag": "value"},
            cred_value={
                "@context": [
                    VC_CONTEXT,
                    "https://www.w3.org/2018/credentials/examples/v1",
                ],
                "id": VC_GIVEN_ID,
                "type": ["VerifiableCredential", "UniversityDegreeCredential"],
                "issuer": VC_ISSUER_ID,
                "identifier": "83627467",
                "name": "University Degree",
                "issuanceDate": "2012-01-01T19:53:24Z",
                "credentialSubject": {
                    "id": VC_SUBJECT_ID,
                    "givenName": "Cai",
                    "familyName": "Leblanc",
                },
                "proof": {
                    "type": "Ed25519Signature2018",
                    "verificationMethod": "did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL",
                    "created": "2021-05-07T08:50:17.626625",
                    "proofPurpose": "assertionMethod",
                    "jws": "eyJhbGciOiAiRWREU0EiLCAiYjY0IjogZmFsc2UsICJjcml0IjogWyJiNjQiXX0..rubQvgig7cN-F6cYn_AJF1BCSaMpkoR517Ot_4pqwdJnQ-JwKXq6d6cNos5JR73E9WkwYISXapY0fYTIG9-fBA",
                },
            },
        )
        await holder.store_credential(record_b)
        record_c = VCRecord(
            contexts=[
                VC_CONTEXT,
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            expanded_types=[
                VC_TYPE,
                "https://example.org/examples#UniversityDegreeCredential",
            ],
            schema_ids=[VC_SCHEMA_ID],
            issuer_id=VC_ISSUER_ID,
            subject_ids=[VC_SUBJECT_ID],
            proof_types=[VC_PROOF_TYPE],
            given_id=VC_GIVEN_ID,
            cred_tags={"tag": "value"},
            cred_value={
                "@context": [
                    VC_CONTEXT,
                    "https://www.w3.org/2018/credentials/examples/v1",
                ],
                "id": VC_GIVEN_ID,
                "type": ["VerifiableCredential", "UniversityDegreeCredential"],
                "issuer": VC_ISSUER_ID,
                "identifier": "83627467",
                "name": "University Degree",
                "issuanceDate": "2009-01-01T19:53:24Z",
                "credentialSubject": {
                    "id": VC_SUBJECT_ID,
                    "givenName": "Cai",
                    "familyName": "Leblanc",
                },
                "proof": {
                    "type": "Ed25519Signature2018",
                    "verificationMethod": "did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL",
                    "created": "2021-05-07T08:50:17.626625",
                    "proofPurpose": "assertionMethod",
                    "jws": "eyJhbGciOiAiRWREU0EiLCAiYjY0IjogZmFsc2UsICJjcml0IjogWyJiNjQiXX0..rubQvgig7cN-F6cYn_AJF1BCSaMpkoR517Ot_4pqwdJnQ-JwKXq6d6cNos5JR73E9WkwYISXapY0fYTIG9-fBA",
                },
            },
        )
        await holder.store_credential(record_c)
        expected = [record_b, record_a, record_c]

        search = holder.search_credentials()
        rows = await search.fetch()
        assert rows == expected
