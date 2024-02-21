import { Page } from '../Main/Page'
import { Post } from './MainPage'
import { useEffect, useRef, useState } from 'react'
import { useBackendClient } from '../../backend-client'


export const AdminPage = () => {
    const client = useBackendClient()
    const [needUpdate, setNeedUpdate] = useState()
    // Новый пост
    const [postText, setPostText] = useState("")
    const [postImage, setPostImage] = useState()
    const onCreateSubmit = async () => {
        try {
            await client.createPost(postImage, postText)
            alert('Пост успешно создан.')
            setPostText('')
            setPostImage(null)
            setNeedUpdate(true)
        } catch (e) {
            alert('Не удалось создать пост.')
        }
    }

    // Самый залайканый и самый задизлайканый посты
    const [likedPost, setLikedPost] = useState()
    const [dislikedPost, setDislikedPost] = useState()
    const [postsQuantity, setPostsQuantity] = useState(0)
    useEffect(() => {
        client.getPosts(1, 1, 'more_likes_first')
            .then(list => setLikedPost(list.items[0]))
        client.getPosts(1, 1, 'more_dislikes_first')
            .then(list => {
                setDislikedPost(list.items[0])
                setPostsQuantity(list.total_quantity)
            })
    },[needUpdate])

    return (
        <Page name='Админка'>
            <div>
                <h4>Новый пост</h4><br/>
                <form className='new-post-layout'>
                    <textarea id="postText" className="new-post-text" placeholder='Текст поста'
                           onChange={event => setPostText(event.target.value)} value={postText} />
                    <input type='file' className='file-input'
                           onChange={(e) => setPostImage(e.target.files[0])}/>
                    <input type='button' className='auth-button' value='Создать' onClick={onCreateSubmit} />
                </form><br/>

                <h4>Всего постов: {postsQuantity}</h4><br/>

                <h4>Больше всего лайков:</h4><br/>
                {likedPost ?
                    <Post data={likedPost} /> : ""}

                <h4>Больше всего дизлайков:</h4><br/>
                {dislikedPost?
                    <Post data={dislikedPost} /> : ""}
            </div>
        </Page>
    )
}
