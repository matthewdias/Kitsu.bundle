## Kitsu Plex Metadata Agent

This plugin will allow you to use Kitsu metadata for a Plex library.

### Installation

- Download and extract the [latest release](https://github.com/matthewdias/Kitsu.bundle/releases/latest).
- Move `Kitsu.bundle` to your Plex [plugins directory](https://support.plex.tv/articles/201106098-how-do-i-find-the-plug-ins-folder/).
- Restart Plex

### Usage

To use the agent, create a new library in Plex and select Kitsu as the metadata agent. There is a TV shows agent, and a movies agent. If you want to enable results for NSFW media, you can sign in to a Kitsu account that has the 'Show Adult Content' option enabled in settings.

#### Convention

You will want to structure your media the same way it is on Kitsu so that matches can be made correctly. A media page on Kitsu should correspond to a single folder for that media, named the same way it is on Kitsu. Your file structure should look like the following:
```
Library
| - Hunter x Hunter (2011)
|   | - 1.mkv
|   | - 2.mkv
|   | - ...
| - Katanagatari
| - Minami-ke Okaeri
```

#### Collections

This agent also sets Plex collection tags to group related shows in an organized way. You can change the settings for your library to hide or show collections. Enabling them will group seasons of a series together (provided we have the proper TheTVDB mappings). By default the collections poster will just be a collage of the shows it contains. If you want, you can edit the collection and add your own poster manually.
