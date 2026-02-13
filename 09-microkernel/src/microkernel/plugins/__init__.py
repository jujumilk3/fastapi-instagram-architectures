from microkernel.plugins.auth.plugin import AuthPlugin
from microkernel.plugins.user.plugin import UserPlugin
from microkernel.plugins.post.plugin import PostPlugin
from microkernel.plugins.follow.plugin import FollowPlugin
from microkernel.plugins.feed.plugin import FeedPlugin
from microkernel.plugins.story.plugin import StoryPlugin
from microkernel.plugins.message.plugin import MessagePlugin
from microkernel.plugins.notification.plugin import NotificationPlugin
from microkernel.plugins.search.plugin import SearchPlugin

PLUGIN_LIST = [
    AuthPlugin(),
    PostPlugin(),
    UserPlugin(),
    FollowPlugin(),
    FeedPlugin(),
    StoryPlugin(),
    MessagePlugin(),
    NotificationPlugin(),
    SearchPlugin(),
]
