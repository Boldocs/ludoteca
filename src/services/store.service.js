import { unauthApi, authApi } from '@/services/api'

import authorizationService from '@/services/authorization.service'

const URL = '/api/store/'

export default {
  getApi(){
    return authorizationService.isAuthenticated() ? authApi : unauthApi
  },
  /**
   * Get all games for the given page
   * @param page
   * @returns {Promise<*>}
   */
  fetchGames(page) {

    return this.getApi()
      .get(URL + 'games/', {
        params: {
          page: page,
        },
      })
      .then(response => response.data)
  },
  /**
   * Get game by game id
   * @param gameId
   * @returns {Promise<*>}
   */
  fetchGame(gameId) {
    return unauthApi
      .get(URL + `games/${gameId}/`)
      .then(response => response.data)
  },

  /**
   * Filter and search games
   * @param params
   * @returns {Promise<AxiosResponse<any>>}
   */
  filterGames(params) {
    return this.getApi()
      .get(URL + 'games/', {
        params: params,
      })
      .then(response => response.data)
  },

  /**
   * Create a new library game
   * @param payload
   * @returns {Promise<AxiosResponse<any>>}
   */
  createGame(payload) {
    return authApi.post(URL + 'games/', payload).then(response => response.data)
  },

  /**
   * Update game information with the given gameId
   * @param gameId
   * @param payload - content to update
   * @returns {Promise<AxiosResponse<any>>}
   */
  updateGame(gameId, payload) {
    return authApi
      .patch(URL + `games/${gameId}/`, payload)
      .then(response => response.data)
  },

  /**
   * Delete game with the given gameId
   * @param gameId
   * @returns {Promise<AxiosResponse<any>>}
   */
  deleteGame(gameId) {
    return authApi
      .delete(URL + `games/${gameId}/`)
      .then(response => response.data)
  },
}
