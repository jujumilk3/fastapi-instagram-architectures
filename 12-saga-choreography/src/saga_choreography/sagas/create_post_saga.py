from saga_choreography.services import hashtag_service, post_service
from saga_choreography.shared.saga import SagaStep


def build_steps(db):
    async def action_create_post(ctx):
        post = await post_service.create_post(
            author_id=ctx["user_id"],
            content=ctx["content"],
            image_url=ctx["image_url"],
            db=db,
        )
        ctx["post_id"] = post.id
        ctx["post"] = post
        return post

    async def compensate_create_post(ctx):
        await post_service.delete_post_by_id(ctx["post_id"], db)

    async def action_extract_hashtags(ctx):
        await hashtag_service.extract_and_save(
            post_id=ctx["post_id"],
            content=ctx["content"],
            db=db,
        )

    async def compensate_extract_hashtags(ctx):
        await hashtag_service.delete_post_hashtags(ctx["post_id"], db)

    return [
        SagaStep(
            name="create_post",
            action=action_create_post,
            compensation=compensate_create_post,
        ),
        SagaStep(
            name="extract_hashtags",
            action=action_extract_hashtags,
            compensation=compensate_extract_hashtags,
        ),
    ]
