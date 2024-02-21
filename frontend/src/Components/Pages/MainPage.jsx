import { useEffect, useState } from 'react'
import { Page } from '../Main/Page'
import { useBackendClient } from '../../backend-client'
import { BiLike, BiDislike } from 'react-icons/bi'
import { AiOutlineArrowLeft, AiOutlineArrowRight } from 'react-icons/ai'

const POSTS_PER_PAGE = 3


export const MainPage = () => {
    const [pageNumber, setPageNumber] = useState(1)
    const [totalPages, setTotalPages] = useState(0)
    const [feedPosts, setFeedPosts] = useState([])
    const client = useBackendClient()

    useEffect(() => {
        window.scrollTo(0, 0);
        client.getPosts(pageNumber, POSTS_PER_PAGE)
            .then(list => {
                setFeedPosts(list.items)
                setTotalPages(Math.ceil(list.total_quantity / POSTS_PER_PAGE))
            })
    }, [pageNumber])

    return (
        <Page name='Главная'>
            <div className='posts-list'>
                {feedPosts.map(
                    post => <Post key={post.id} data={post} />
                )}
            </div>
            <div className='posts-pages-switcher-layout'>
                {pageNumber !== 1 ?
                    <AiOutlineArrowLeft className='posts-pages-switcher'
                                        onClick={_ => setPageNumber(page => page - 1)} /> : ""}
                {pageNumber < totalPages ?
                    <AiOutlineArrowRight className='posts-pages-switcher'
                                         onClick={_ => setPageNumber(page => page + 1)} /> : ""}

            </div>
        </Page>
    )
}

const Reaction = {
    Like: 'like',
    Dislike: 'dislike',
    None: null,
}

export const Post = ({data}) => {
    const [likesQuantity, setLikesQuantity] = useState(data.likes_quantity)
    const [dislikesQuantity, setDislikesQuantity] = useState(data.dislikes_quantity)
    const client = useBackendClient()

    const [reaction, setReaction] = useState(data.rate)
    const switchReaction = async (newReaction) => {
        if (reaction === newReaction) {
            return
        }

        await client.setReactionToPost(data.id, newReaction)

        let deltaLikes = 0;
        let deltaDislikes = 0;
        if (reaction === Reaction.Like) {
            deltaLikes -= 1
        } else if (reaction === Reaction.Dislike) {
            deltaDislikes -= 1
        }
        if (newReaction === Reaction.Like) {
            deltaLikes += 1
        } else if (newReaction === Reaction.Dislike) {
            deltaDislikes += 1
        }

        setLikesQuantity(likes => likes + deltaLikes)
        setDislikesQuantity(dislikes => dislikes + deltaDislikes)
        setReaction(newReaction)
    }
    console.log(data.created_at)
    return (
        <div className='post-layout'>
            <img src={data.image_url} alt="Can't load image." className='post-image'/>
            <div className='post-description-layout'>
                <div className='post-description-text'>
                    {data.text}
                </div>
                <div className='post-reactions-layout'>
                    <div className='post-reaction'>
                        <b className='post-reaction-quantity'>{likesQuantity}</b>
                        {reaction === Reaction.Like ?
                            <BiLike onClick={() => switchReaction(Reaction.None)} className='post-reaction-icon-clicked post-reaction-icon' />
                            : <BiLike onClick={() => switchReaction(Reaction.Like)} className='post-reaction-icon' />
                        }
                    </div>
                    <div className='post-reaction'>
                        <b className='post-reaction-quantity'>{dislikesQuantity}</b>
                        {reaction === Reaction.Dislike ?
                            <BiDislike onClick={() => switchReaction(Reaction.None)} className='post-reaction-icon-clicked post-reaction-icon' />
                            : <BiDislike onClick={() => switchReaction(Reaction.Dislike)} className='post-reaction-icon' />
                        }
                    </div>
                </div>
            </div>
        </div>
    )
}
