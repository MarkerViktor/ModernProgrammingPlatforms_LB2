import axios from 'axios'


export class BackendClient {
    client = axios.create({
        baseURL: '/api/',
        headers: {
            'Accept': 'application/json',
        },
        withCredentials: true,
    })

    async signIn(login, password) {
        const form = new URLSearchParams({
            'login': login,
            'password': password,
        })
        const response = await this.client.post('/sign_in', form)
        return response.data
    }

    async signUp(firstName, lastName, login, password) {
        const form = new URLSearchParams({
            'first_name': firstName,
            'last_name': lastName,
            'login': login,
            'password': password
        })
        await this.client.post('/sign_up', form)
    }

    async getPosts(pageNumber, perPage, order = 'new_first') {
        const queryParams = {
            'page': pageNumber,
            'per_page': perPage,
            'order': order,
        }
        const response = await this.client.get('/posts', {params: queryParams})
        return response.data
    }

    async createPost(imageBlob, text) {
        const formData = new FormData()
        formData.append('image', imageBlob)
        formData.append('text', text)

        await this.client.post('/posts', formData)
    }

    async setReactionToPost(postId, reaction) {
        const reactionPayload = {
            'rate': reaction,
        }
        await this.client.put(`/posts/${postId}/rate`, reactionPayload)
    }

    async signOut() {
        await this.client.post('/sign_out')
    }
}


export const useBackendClient = () => {
    return new BackendClient()
}
