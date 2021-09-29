const flatten = require('flat');

const Client = require('bitcoin-core');
const client = new Client();

//client.getTransactionByHash('fa5e440a221db13575f32e28dd718f3159d98736116cccb0396836882da9e4ed').then(console.log).catch(console.error);

let rawFundTx = {"txid":"307f7ab041d0c084de25e0a51742743ae7113db550b91cea5c1f7f9df49e8497","hash":"fa5e440a221db13575f32e28dd718f3159d98736116cccb0396836882da9e4ed","version":1,"size":531,"vsize":288,"weight":1152,"locktime":0,"vin":[{"txid":"0740c4fdb0f1d0715740c1b1d0faf75b57478c048f318076fc27545d5c5f175e","vout":1,"scriptSig":{"asm":"","hex":""},"txinwitness":["304502210085a68f95b7805eb68bcf26a2174e5486216c7a4be8377dac340c809634e9a3f102200703cbb9f70f4e38a83eca09783e9a5e3755476a3848843ed570b7ba3d9b42a901","03849ad2f9eed7da4adc11e627fad42d13d8aa3b30da252d97e24992c53cf82f35"],"sequence":4294967295},{"txid":"be980cceb4c3424d5a6b388e7ac7545d6dbb1ca4978f841a35c530dd6b27aa1c","vout":0,"scriptSig":{"asm":"","hex":""},"txinwitness":["3044022074d29d0b2f71118aaedc7639b6603f0d287a82131c062b968ae18b53ecf503e102203ce864830b11ceeb68cf9f0a72746b2b0592839ccd2d44a232fbbb72026bc4b301","022fe46ac3aa79bda14f6f0df3c83430b48c783f0c32f43a237655d1cc757dca32"],"sequence":4294967295},{"txid":"cebfea99aa34f5ca1cb3adabc9648736b0624523e4f3da3f29a7b4a0d69f730d","vout":1,"scriptSig":{"asm":"","hex":""},"txinwitness":["304402201210b1e0d81b28aeec6ec855523995a3fcd8f2d6c0e34969c900891c3c7f1e5a02205d4e250a645ef408307bb07f3087d138343a9019759cd184b1ab39f881d5f66201","039d888efa30b109553324b35364a7422bd92be93db3522200c61ecb52661e3907"],"sequence":4294967295}],"vout":[{"value":0.00020000,"n":0,"scriptPubKey":{"asm":"0 749c9a82c4cab566cb87056c343ae637a5fc35d5d6743d76263a22e1b1445cf5","hex":"0020749c9a82c4cab566cb87056c343ae637a5fc35d5d6743d76263a22e1b1445cf5","reqSigs":1,"type":"witness_v0_scripthash","addresses":["bc1qwjwf4qkye26kdju8q4krgwhxx7jlcdw46e6r6a3x8g3wrv2ytn6skdjvfs"]}},{"value":0.00026131,"n":1,"scriptPubKey":{"asm":"0 2847e20a5b738ccd4d427ca53d038d65f370948a","hex":"00142847e20a5b738ccd4d427ca53d038d65f370948a","reqSigs":1,"type":"witness_v0_keyhash","addresses":["bc1q9pr7yzjmwwxv6n2z0jjn6qudvhehp9y2rjth6n"]}}],"hex":"010000000001035e175f5c5d5427fc7680318f048c47575bf7fad0b1c1405771d0f1b0fdc440070100000000ffffffff1caa276bdd30c5351a848f97a41cbb6d5d54c77a8e386b5a4d42c3b4ce0c98be0000000000ffffffff0d739fd6a0b4a7293fdaf3e4234562b0368764c9abadb31ccaf534aa99eabfce0100000000ffffffff02204e000000000000220020749c9a82c4cab566cb87056c343ae637a5fc35d5d6743d76263a22e1b1445cf513660000000000001600142847e20a5b738ccd4d427ca53d038d65f370948a0248304502210085a68f95b7805eb68bcf26a2174e5486216c7a4be8377dac340c809634e9a3f102200703cbb9f70f4e38a83eca09783e9a5e3755476a3848843ed570b7ba3d9b42a9012103849ad2f9eed7da4adc11e627fad42d13d8aa3b30da252d97e24992c53cf82f3502473044022074d29d0b2f71118aaedc7639b6603f0d287a82131c062b968ae18b53ecf503e102203ce864830b11ceeb68cf9f0a72746b2b0592839ccd2d44a232fbbb72026bc4b30121022fe46ac3aa79bda14f6f0df3c83430b48c783f0c32f43a237655d1cc757dca320247304402201210b1e0d81b28aeec6ec855523995a3fcd8f2d6c0e34969c900891c3c7f1e5a02205d4e250a645ef408307bb07f3087d138343a9019759cd184b1ab39f881d5f6620121039d888efa30b109553324b35364a7422bd92be93db3522200c61ecb52661e390700000000"};
let rawClosTx = {"txid":"904dc9db1a691756b39ecb6e9c47ec0688fd5dcf7cc24cd7b5056cbe72d74a62","hash":"9a6f894786f0367f9e9a4d4c7e40fe2194affd3ae54110e52262eb20e53d255a","version":2,"size":334,"vsize":169,"weight":673,"locktime":0,"vin":[{"txid":"307f7ab041d0c084de25e0a51742743ae7113db550b91cea5c1f7f9df49e8497","vout":0,"scriptSig":{"asm":"","hex":""},"txinwitness":["","3045022100c6bc132bc3a245f727dd986e8b80184b91d353d0c90429e46d7e32d54c5825fd02206006589f9968b19d5f9c0c2736c3752cc3a41dab70ebd259a1d23d8d3e83196401","304402201d96b1fbc7c0452b2f3aef179b482ca68f2f14d7a9daaabd92a4770ef466ee0602205c24c1ed5449fa2d44066e14043dd82eae943c12c379eb26c4b3a31c05492c2701","52210253822504e6123017ef0f5240ceacfa39bf38f5df6dbe65f1ec8ff9b3eb006e9f2102ac00432d10c4e8f4e548f6f8c8bcddc8c92e07079f46b20f6430ca7c8372582452ae"],"sequence":4294967295}],"vout":[{"value":0.00005000,"n":0,"scriptPubKey":{"asm":"0 6a3d04a6e3f2658714ace5f07a478d48c40098a8","hex":"00146a3d04a6e3f2658714ace5f07a478d48c40098a8","reqSigs":1,"type":"witness_v0_keyhash","addresses":["bc1qdg7sffhr7fjcw99vuhc853udfrzqpx9gq8qcmz"]}},{"value":0.00013820,"n":1,"scriptPubKey":{"asm":"0 6f3cd16cc8b7d876481ef13d61485f19694a90d8","hex":"00146f3cd16cc8b7d876481ef13d61485f19694a90d8","reqSigs":1,"type":"witness_v0_keyhash","addresses":["bc1qdu7dzmxgklv8vjq77y7kzjzlr9554yxcde80dt"]}}],"hex":"0200000000010197849ef49d7f1f5cea1cb950b53d11e73a744217a5e025de84c0d041b07a7f300000000000ffffffff0288130000000000001600146a3d04a6e3f2658714ace5f07a478d48c40098a8fc350000000000001600146f3cd16cc8b7d876481ef13d61485f19694a90d80400483045022100c6bc132bc3a245f727dd986e8b80184b91d353d0c90429e46d7e32d54c5825fd02206006589f9968b19d5f9c0c2736c3752cc3a41dab70ebd259a1d23d8d3e8319640147304402201d96b1fbc7c0452b2f3aef179b482ca68f2f14d7a9daaabd92a4770ef466ee0602205c24c1ed5449fa2d44066e14043dd82eae943c12c379eb26c4b3a31c05492c27014752210253822504e6123017ef0f5240ceacfa39bf38f5df6dbe65f1ec8ff9b3eb006e9f2102ac00432d10c4e8f4e548f6f8c8bcddc8c92e07079f46b20f6430ca7c8372582452ae00000000"};

console.log(flatten(rawFundTx));
console.log(flatten(rawClosTx));