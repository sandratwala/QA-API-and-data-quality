import pytest

POST_FIELDS = {"userId", "id", "title", "body"}
COMMENT_FIELDS = {"postId", "id", "name", "email", "body"}
TOTAL_POSTS = 100


@pytest.mark.positive
class TestReadPosts:
    def test_list_posts_returns_all_posts(self, api):
        response = api.get("/posts")

        assert response.status_code == 200
        posts = response.json()
        assert isinstance(posts, list)
        assert len(posts) == TOTAL_POSTS

    def test_post_ids_are_unique(self, api):
        posts = api.get("/posts").json()
        ids = [post["id"] for post in posts]

        assert len(ids) == len(set(ids))

    def test_single_post_has_expected_schema_and_types(self, api):
        response = api.get("/posts/1")

        assert response.status_code == 200
        post = response.json()
        assert set(post) == POST_FIELDS
        assert post["id"] == 1
        assert isinstance(post["userId"], int)
        assert isinstance(post["title"], str) and post["title"].strip()
        assert isinstance(post["body"], str) and post["body"].strip()

    def test_response_is_json(self, api):
        response = api.get("/posts/1")

        assert "application/json" in response.headers["Content-Type"]

    def test_response_time_is_acceptable(self, api):
        response = api.get("/posts/1")

        assert response.elapsed.total_seconds() < 5

    def test_filter_by_user_returns_only_that_users_posts(self, api):
        response = api.get("/posts", params={"userId": 1})

        assert response.status_code == 200
        posts = response.json()
        assert len(posts) > 0
        assert all(post["userId"] == 1 for post in posts)

    def test_nested_and_filtered_routes_return_the_same_comments(self, api):
        nested = api.get("/posts/1/comments").json()
        filtered = api.get("/comments", params={"postId": 1}).json()

        assert nested == filtered
        assert len(nested) > 0
        for comment in nested:
            assert set(comment) == COMMENT_FIELDS
            assert comment["postId"] == 1
            assert "@" in comment["email"]


@pytest.mark.positive
class TestWritePosts:
    def test_create_post_returns_201_and_echoes_data(self, api, new_post):
        response = api.post("/posts", json=new_post)

        assert response.status_code == 201
        created = response.json()
        assert isinstance(created["id"], int)
        for field, value in new_post.items():
            assert created[field] == value

    def test_replace_post_with_put(self, api, new_post):
        response = api.put("/posts/1", json={**new_post, "id": 1})

        assert response.status_code == 200
        assert response.json()["title"] == new_post["title"]
        assert response.json()["id"] == 1

    def test_partial_update_with_patch_changes_only_given_field(self, api):
        original = api.get("/posts/1").json()

        response = api.patch("/posts/1", json={"title": "Patched title"})

        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "Patched title"
        assert updated["body"] == original["body"]
        assert updated["userId"] == original["userId"]

    def test_delete_post(self, api):
        response = api.delete("/posts/1")

        assert response.status_code == 200


@pytest.mark.negative
class TestInvalidInput:
    @pytest.mark.parametrize("post_id", ["0", "-1", "101", "abc", "99999999999"])
    def test_unknown_post_id_returns_404(self, api, post_id):
        response = api.get(f"/posts/{post_id}")

        assert response.status_code == 404
        assert response.json() == {}

    def test_unknown_route_returns_404(self, api):
        response = api.get("/postss")

        assert response.status_code == 404

    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="BUG-API-01: API accepts a post with no title or body", strict=False)
    def test_create_post_without_required_fields_is_rejected(self, api):
        response = api.post("/posts", json={})

        assert response.status_code in (400, 422)

    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="BUG-API-02: API accepts a userId that is not a number", strict=False)
    def test_create_post_with_wrong_type_is_rejected(self, api, new_post):
        response = api.post("/posts", json={**new_post, "userId": "not-a-number"})

        assert response.status_code in (400, 422)

    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="BUG-API-03: updating a post that does not exist does not return 404", strict=False)
    def test_update_unknown_post_returns_404(self, api, new_post):
        response = api.put("/posts/9999", json=new_post)

        assert response.status_code == 404


@pytest.mark.edge
class TestEdgeCases:
    def test_filter_with_no_matches_returns_empty_list(self, api):
        response = api.get("/posts", params={"userId": 9999})

        assert response.status_code == 200
        assert response.json() == []

    def test_filter_with_non_numeric_value_returns_empty_list_not_error(self, api):
        response = api.get("/posts", params={"userId": "abc"})

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.parametrize("limit, expected", [(1, 1), (5, 5), (1000, TOTAL_POSTS)])
    def test_limit_parameter(self, api, limit, expected):
        response = api.get("/posts", params={"_limit": limit})

        assert response.status_code == 200
        assert len(response.json()) == expected

    def test_unicode_and_emoji_survive_round_trip(self, api, new_post):
        payload = {**new_post, "title": "Murakoze cyane — Kigali ✓ 🚀", "body": "Ñandú, naïve, 東京"}

        response = api.post("/posts", json=payload)

        assert response.status_code == 201
        assert response.json()["title"] == payload["title"]
        assert response.json()["body"] == payload["body"]

    def test_very_long_title_is_accepted_unchanged(self, api, new_post):
        long_title = "A" * 10_000

        response = api.post("/posts", json={**new_post, "title": long_title})

        assert response.status_code == 201
        assert response.json()["title"] == long_title

    def test_special_characters_are_not_interpreted(self, api, new_post):
        payload = {**new_post, "title": "'; DROP TABLE posts; -- <script>alert(1)</script>"}

        response = api.post("/posts", json=payload)

        assert response.status_code == 201
        assert response.json()["title"] == payload["title"]
        assert api.get("/posts").status_code == 200
