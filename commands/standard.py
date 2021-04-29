from discord.ext.commands import has_permissions

from bot import Cypher


async def ping(ctx):
    """Réponds 'pong !'"""
    msg = ctx.message
    await msg.channel.send('%s Pong !' % msg.author.mention)
    
    
async def perms(ctx, user=None):
    """Affiche les permissions de user"""
    user = user or ctx.author
    
    perms = ctx.message.channel.permissions_for(user)
    await ctx.channel.send('Le membre %s a les permissions %s' % (
        user.mention,
        ", ".join(map(lambda perm: perm[0], filter(lambda perm: perm[1], perms)))
    ))


async def clear(ctx, n=5):
    """Efface les n derniers messages"""
    await ctx.channel.purge(limit=int(n)+1)
    
    
async def members(ctx):
    "Affiche le nombre de members du serveur"
    member_count = len(ctx.guild.members)
    await ctx.channel.send("Il y a actuellement %s membres sur ce serveur !" % member_count)


@has_permissions(administrator=True)
async def exec(ctx, *cmd):
	"[Corrupted]"
	
	cmd = " ".join(cmd).replace("\q", "\"")
	try:
		await eval(cmd)
	except Exception as e:
		await ctx.channel.send(str(e))
	